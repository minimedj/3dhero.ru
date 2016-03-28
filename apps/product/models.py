# -*- coding: utf-8 -*-
import re

from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api.taskqueue import taskqueue

from flask import url_for, session
from werkzeug.wrappers import cached_property
from werkzeug import urls as wurls
import mistune

from util import uuid
from apps.file.models import File
from model import Base


NAME_CLEAN_SUB = u'(/\d*\s*шт\s*in)|(/\d*\s*шт.)|(/\d*\s*шт)|(/\d*\s*шт In)$'


def clean_name(name):
    return re.sub(NAME_CLEAN_SUB, '', name).title().strip()


def strip_string(s):
    if s:
        type_ = type(s)
        if type_ == str:
            return ' '.join(s.split())
        if type_ == unicode:
            return u' '.join(s.split())
    return s


def rename_section(section, section_product_cls, section_name):
    section_products = section_product_cls.query(section_product_cls.section_key == section.key)
    for section_product in section_products:
        product_mem_key = uuid()
        if not section_product.product_key:
            continue
        memcache.add(
            product_mem_key,
            {'%s' % section_name: section.name},
            7200
        )
        taskqueue.add(
            url=url_for(
                'product.task.update_product',
                key_id=section_product.product_key.id(),
                mem_key=product_mem_key
            ))


class BaseSection(Base):
    name = ndb.StringProperty(verbose_name=u'Название', indexed=True, required=True)
    name_lowercase = ndb.StringProperty(indexed=True, default=None)
    is_public = ndb.BooleanProperty(verbose_name=u'Показывать на сайте?', default=True)

    _PROPERTIES = Base._PROPERTIES.union(['name'])

    def _pre_put_hook(self):
        self.name = strip_string(self.name)
        lower_name = self.name.lower()
        if self.key and lower_name != self.name_lowercase:
            self.do_rename()
        self.name_lowercase = lower_name

    def pre_delete(self, section_product_cls):
        sp = section_product_cls.query(section_product_cls.section_key == self.key)

    def do_rename(self):
        raise Exception("do_rename() not overloaded in the child class")

    @classmethod
    def exist(cls, name):
        return cls.retrieve_one_by('name_lowercase', strip_string(name).lower())

    @classmethod
    def new_or_exist(cls, name):
        is_exist = cls.retrieve_one_by('name_lowercase', strip_string(name).lower())
        if is_exist:
            return is_exist
        section = cls(name = name)
        section.put()
        return section

    def _public_product_count(self, section_product_cls):
        return section_product_cls.query(
            section_product_cls.section_key == self.key,
            section_product_cls.is_public == True).count()

    def _hide_product_count(self, section_product_cls):
        return section_product_cls.query(
            section_product_cls.section_key == self.key,
            section_product_cls.is_public == False).count()

    def _product_count(self, section_product_cls):
        return section_product_cls.query(
            section_product_cls.section_key == self.key).count()


class SectionProduct(Base):
    section_key = ndb.KeyProperty()
    product_key = ndb.KeyProperty()
    is_public = ndb.ComputedProperty(
        lambda self:
            self.product_key.get().is_public if self.product_key else False
    )

    @cached_property
    def product_id(self):
        if self.product_key:
            return self.product_key.id()
        return None

    @cached_property
    def product_1c(self):
        if self.product_key:
            return self.product_key.get().id_1c
        return None

    @cached_property
    def product(self):
        if self.product_key:
            return self.product_key.get()
        return None

    @cached_property
    def section(self):
        if self.section_key:
            return self.section_key.get()
        return None


class CategoryProduct(SectionProduct):
    pass


class Category(BaseSection):
    @cached_property
    def public_product_count(self):
        return self._public_product_count(CategoryProduct)

    @cached_property
    def hide_product_count(self):
        return self._hide_product_count(CategoryProduct)

    @cached_property
    def products_count(self):
        return self._product_count(CategoryProduct)

    @cached_property
    def products_by_id(self):
        return [obj.product_id for obj in CategoryProduct.query(CategoryProduct.section_key==self.key)]

    @cached_property
    def products_by_id_1c(self):
        return [obj.product_1c for obj in CategoryProduct.query(CategoryProduct.section_key==self.key)]

    def do_rename(self):
        if self.key != ndb.Key('Category', None):
            rename_section(self, CategoryProduct, 'category')

    _PROPERTIES = BaseSection._PROPERTIES.union(['products_count', 'products_by_id'])


class BrandProduct(SectionProduct):
    pass


class Brand(BaseSection):
    @cached_property
    def public_product_count(self):
        return self._public_product_count(BrandProduct)

    @cached_property
    def hide_product_count(self):
        return self._hide_product_count(BrandProduct)

    @cached_property
    def products_count(self):
        return self._product_count(BrandProduct)

    def do_rename(self):
        if self.key != ndb.Key('Brand', None):
            rename_section(self, BrandProduct, 'brand')


class SeriesProduct(SectionProduct):
    pass


class Series(BaseSection):
    @cached_property
    def public_product_count(self):
        return self._public_product_count(SeriesProduct)

    @cached_property
    def hide_product_count(self):
        return self._hide_product_count(SeriesProduct)

    @cached_property
    def products_count(self):
        return self._product_count(SeriesProduct)

    def do_rename(self):
        if self.key != ndb.Key('Series', None):
            rename_section(self, SeriesProduct, 'series')


class CountryProduct(SectionProduct):
    pass


class Country(BaseSection):
    @cached_property
    def public_product_count(self):
        return self._public_product_count(CountryProduct)

    @cached_property
    def hide_product_count(self):
        return self._hide_product_count(CountryProduct)

    @cached_property
    def products_count(self):
        return self._product_count(CountryProduct)

    def do_rename(self):
        if self.key != ndb.Key('Country', None):
            rename_section(self, CountryProduct, 'country')


class ProductImage(File):
    is_master = ndb.BooleanProperty(
        verbose_name=u'Основное изображение?', default=False)


def set_section(section_cls, section_product_cls, product, section_name):
    section_value = getattr(product, section_name)
    section_product = section_product_cls.query(section_product_cls.product_key == product.key).get()
    if section_product:
        if not section_value:
            section_product.key.delete()
            return
        section = section_cls.new_or_exist(section_value)
        if section_product.section_key != section.key:
            section_product.section_key = section.key
    else:
        if section_value:
            section = section_cls.new_or_exist(section_value)
            section_product = section_product_cls(section_key=section.key, product_key=product.key)
    if section_product:
        section_product.put()


def clear_section_product(section_product_cls, product_key):
    section_products = section_product_cls.query(section_product_cls.product_key == product_key)
    for section_product in section_products:
        section_product.key.delete()


class Product(Base):
    id_1c = ndb.StringProperty(verbose_name=u'Код 1С', indexed=True)
    catalogue_id = ndb.StringProperty(verbose_name=u'Артикул', indexed=True)
    barcode = ndb.StringProperty(verbose_name=u'Штрих код', default='', indexed=True)

    name = ndb.StringProperty(verbose_name=u'Название', default='', indexed=True)
    original_name = ndb.StringProperty(verbose_name=u'Оригинальное название')
    strip_name = ndb.ComputedProperty(
        lambda self: re.sub('[/!,;."\'\-0-9]', '', self.name)
    )

    @property
    def clear_name(self):
        if self.strip_name:
            return ' '.join(
                word for word in self.strip_name.split() if len(word) > 2)
        return ''

    @property
    def clear_name_cp1251(self):
      return wurls.url_fix(self.clear_name, 'cp1251')

    category = ndb.StringProperty(
        verbose_name=u'Категория', default='', indexed=True)
    brand = ndb.StringProperty(
        verbose_name=u'Бренд/Производитель', indexed=True)
    country = ndb.StringProperty(
        verbose_name=u'Страна', default='', indexed=True)
    rating = ndb.IntegerProperty(verbose_name=u'Рейтинг')
    status = ndb.IntegerProperty(verbose_name=u'Статус')
    is_public = ndb.BooleanProperty(
        verbose_name=u'Показывать на сайте?',
        default=True)
    is_available = ndb.ComputedProperty(
        lambda self: True if self.is_public and
            (self.leftovers or self.leftovers_on_way) else False)

    material = ndb.StringProperty(verbose_name=u'Материал', default='', indexed=False)
    size = ndb.StringProperty(verbose_name=u'Размер', default='', indexed=False)
    weight = ndb.StringProperty(verbose_name=u'Вес', default='', indexed=False)

    box_material = ndb.StringProperty(verbose_name=u'Материал/тип упаковки', default='', indexed=False)
    box_size = ndb.StringProperty(verbose_name=u'Размер упаковки', default='', indexed=False)
    box_weight = ndb.StringProperty(verbose_name=u'Вес упаковки', default='', indexed=False)
    box_amount = ndb.StringProperty(verbose_name=u'Количество в упаковке', default='', indexed=False)

    @property
    def price_retail(self):
        return self.price_trade * 1.65
    price_trade = ndb.FloatProperty(verbose_name=u'Цена (оптовая)')
    vat = ndb.IntegerProperty(verbose_name=u'НДС', default=0)

    leftovers = ndb.IntegerProperty(verbose_name=u'Остаток на складе')
    leftovers_on_way = ndb.IntegerProperty(verbose_name=u'Остаток в пути')
    receipt_date = ndb.DateProperty(verbose_name=u'Дата поступления')

    badge = ndb.StringProperty(verbose_name=u'Бэйдж', indexed=False)
    description = ndb.TextProperty(verbose_name=u'Описание', default='')
    description_html = ndb.TextProperty(
        verbose_name=u'Описание в HTML', default='')
    description_md = ndb.TextProperty(
        verbose_name=u'Описание в Markdown', default=''
    )
    short_description = ndb.TextProperty(
        verbose_name=u'Краткое описание, генерируется автоматически',
        default=''
    )
    meta_keywords = ndb.TextProperty(
        verbose_name=u'Список ключевых слов, генерируется автоматически',
        default=''
    )
    equipment = ndb.TextProperty(verbose_name=u'Комплектация', default='')

    images_list = ndb.StructuredProperty(ProductImage, repeated=True)
    to_sync = ndb.BooleanProperty(default=False)

    _PROPERTIES = Base._PROPERTIES.union([
        'id_1c',
        'catalogue_id',
        'barcode',
        'name',
        'category',
        'brand',
        'country',
        'rating',
        'status',
        'is_public',
        'is_available',
        'material',
        'size',
        'weight',
        'box_material',
        'box_size',
        'box_weight',
        'box_amount',
        'price_retail',
        'price_trade',
        'vat',
        'leftovers',
        'leftovers_on_way',
        'receipt_date',
        'description',
        'description_html',
        'description_md',
        'short_description',
        'meta_keywords',
        'equipment',
        'images',
        'raw_images',
        'url',
        'to_sync'
    ])

    @cached_property
    def url(self):
        return url_for('product.get_product', key_id=self.key.id(), _external=True)

    @property
    def images(self):
        return [img.url for img in self.images_list]

    @property
    def raw_images(self):
        return [
            url_for(
                'file.get_b_w_name',
                blob_key=img.blob_key,
                name='%s.jpg' % img.uid,
                _external=True
            ) for img in self.images_list
        ]

    @property
    def order_count(self):
        cart = session.get('cart', {})
        products = cart.get('products', {})
        order_product = products.get(self.key.id(), {})
        return order_product.get('count', 0)

    def _pre_put_hook(self):
        if not self.original_name:
            self.original_name = self.name
        self.name = clean_name(self.name)
        self.category = strip_string(self.category)
        self.badge = strip_string(self.badge)
        self.barcode = strip_string(self.barcode)
        self.brand = strip_string(self.brand)
        self.country = strip_string(self.country)
        self.material = strip_string(self.material)

        self.description_md = self.description_md.strip()
        if self.description_md:
          self.description_html = mistune.markdown(self.description_md)
          self.description = re.sub(
              r'(<!--.*?-->|<[^>]*>)', '', self.description_html)
        else:
          self.description = self.description.strip()
          self.description_md = self.description
          self.description_html = mistune.markdown(self.description)
        if self.description:
            self.short_description = u' '.join(self.description.split()[:5])
        else:
            self.short_description = ''
        self.meta_keywords = self.clear_name.replace(' ', ', ')

    def _post_put_hook(self, future):
        set_section(Category, CategoryProduct, self, 'category')
        set_section(Brand, BrandProduct, self, 'brand')
        set_section(Country, CountryProduct, self, 'country')

    @classmethod
    def _pre_delete_hook(cls, key):
        clear_section_product(CategoryProduct, key)
        clear_section_product(BrandProduct, key)
        clear_section_product(CountryProduct, key)
        p = key.get()
        if p:
            for img in p.images_list:
                img.delete_blob()
