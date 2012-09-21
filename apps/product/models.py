# -*- coding: utf-8 -*-
from flask import url_for
from werkzeug.wrappers import cached_property
from google.appengine.ext import ndb, db
from google.appengine.api import memcache
from google.appengine.api.taskqueue import taskqueue
from util import uuid
from apps.file.models import File
from model import Base

def strip_string(s):
    if s:
        type_ = type(s)
        if type_ == str:
            return ' '.join(s.split())
        if type_ == unicode:
            return ' '.join(s.split())
    return s

def rename_section(section, section_name):
    if not section:
        return
    for product in section.all_products:
        product_mem_key = uuid()
        memcache.add(
            product_mem_key,
            {'%s' % section_name: section.name},
            7200
        )
        taskqueue.add(
            url=url_for(
                'product.task.update_product',
                key_id=product,
                mem_key=product_mem_key
            ))

class BaseSection(Base):
    name = ndb.StringProperty(verbose_name=u'Название', indexed=True, required=True)
    name_lowercase = ndb.StringProperty(indexed=True, default=None)

    products = ndb.IntegerProperty(repeated=True)
    hide_products = ndb.IntegerProperty(repeated=True)

    is_products = ndb.ComputedProperty(lambda self: True if self.products_count else False)
    is_hide_products = ndb.ComputedProperty(lambda self: True if self.hide_products_count else False)
    is_all_products = ndb.ComputedProperty(lambda self: True if self.all_products_count else False)
    products_count = ndb.ComputedProperty(lambda self: len(self.products))
    hide_products_count = ndb.ComputedProperty(lambda self: len(self.hide_products))
    all_products_count = ndb.ComputedProperty(lambda self: len(self.all_products))

    is_public = ndb.BooleanProperty(verbose_name=u'Показывать на сайте?', default=True)

    def _pre_put_hook(self):
        self.name = strip_string(self.name)
        lower_name = self.name.lower()
        if lower_name != self.name_lowercase:
            self.do_rename()
        self.name_lowercase = lower_name

    def do_rename(self):
        raise Exception("do_rename() not overloaded in the child class")

    @property
    def all_products(self):
        return self.products + self.hide_products

    @classmethod
    def get_exist(cls, name):
        if not name:
            return None
        is_exist = cls.query().filter(cls.name_lowercase == name.lower())
        if is_exist.count():
            return is_exist.get()
        return None

    @classmethod
    def new_or_exist(cls, name):
        is_exist = cls.get_exist(name)
        if is_exist:
            return is_exist
        section = cls(name = name)
        return section

    @classmethod
    def delete_product(cls, name, key_id):
        is_exist = cls.get_exist(name)
        if is_exist is None:
            return False
        flag = False
        if key_id in is_exist.products:
            is_exist.products.remove(key_id)
            flag = True
        if key_id in is_exist.hide_products:
            is_exist.hide_products.remove(key_id)
            flag = True
        if flag:
            is_exist.put()

class Category(BaseSection):
    def do_rename(self):
        rename_section(self, 'category')

    @classmethod
    def _pre_delete_hook(cls, key):
        category = key.get()
        if category:
            for product in category.all_products:
                product_mem_key = uuid()
                memcache.add(
                    product_mem_key,
                    {'category': ''},
                    7200
                )
                taskqueue.add(
                    url=url_for(
                        'product.task.update_product',
                        key_id=product,
                        mem_key=product_mem_key)
                )


class Genre(BaseSection):
    def do_rename(self):
        rename_section(self, 'genre')

    @classmethod
    def _pre_delete_hook(cls, key):
        genre = key.get()
        if genre:
            for product in genre.all_products:
                product_mem_key = uuid()
                memcache.add(
                    product_mem_key,
                    {'genre': ''},
                    7200
                )
                taskqueue.add(
                    url=url_for(
                        'product.task.update_product',
                        key_id=product,
                        mem_key=product_mem_key)
                )

class Series(BaseSection):
    def do_rename(self):
        rename_section(self, 'series')

    @classmethod
    def _pre_delete_hook(cls, key):
        series = key.get()
        if series:
            for product in series.all_products:
                product_mem_key = uuid()
                memcache.add(
                    product_mem_key,
                    {'series': ''},
                    7200
                )
                taskqueue.add(
                    url=url_for(
                        'product.task.update_product',
                        key_id=product,
                        mem_key=product_mem_key)
                )

class Brand(BaseSection):
    def do_rename(self):
        rename_section(self, 'brand')

    @classmethod
    def _pre_delete_hook(cls, key):
        brand = key.get()
        if brand:
            for product in brand.all_products:
                product_mem_key = uuid()
                memcache.add(
                    product_mem_key,
                    {'brand': ''},
                    7200
                )
                taskqueue.add(
                    url=url_for(
                        'product.task.update_product',
                        key_id=product,
                        mem_key=product_mem_key)
                )

def _unique_section_products(section):
    prs = section.products
    hide_prs =section.hide_products
    section.products = list(set(section.products))
    section.hide_products = list(set(section.hide_products))
    if prs != section.products or hide_prs != section.hide_products:
        return True
    return False

def _clear_section(section, key_id):
    flag = False
    if section:
        flag = _unique_section_products(section)
        if key_id in section.products:
            section.products.remove(key_id)
            flag = True
        if key_id in section.hide_products:
            section.hide_products.remove(key_id)
            flag = True
    return flag

def _set_section(section, key_id, is_public=True):
    flag = False
    if section:
        if is_public:
            if key_id in section.hide_products:
                section.hide_products.remove(key_id)
                flag = True
            if key_id not in section.products:
                section.products.append(key_id)
                flag = True
        else:
            if key_id in section.products:
                section.products.remove(key_id)
                flag = True
            if key_id not in section.hide_products:
                section.hide_products.append(key_id)
                flag = True
    return flag

class ProductImage(File):
    is_master = ndb.BooleanProperty(verbose_name=u'Основное изображение?', default=False)

class Product(Base):
    id_1c = ndb.StringProperty(verbose_name=u'Код 1С', indexed=True)
    catalogue_id = ndb.StringProperty(verbose_name=u'Артикул', indexed=True)
    barcode = ndb.StringProperty(verbose_name=u'Штрих код', default='', indexed=True)

    name = ndb.StringProperty(verbose_name=u'Название', default='', indexed=True)
    category = ndb.StringProperty(verbose_name=u'Категория', default='', indexed=True)
    genre = ndb.StringProperty(verbose_name=u'Жанр', default='', indexed=True)
    series = ndb.StringProperty(verbose_name=u'Серия', default='', indexed=True)

    brand = ndb.StringProperty(verbose_name=u'Брэнд/Производитель', indexed=True)
    country = ndb.StringProperty(verbose_name=u'Страна', default='', indexed=True)

    rating = ndb.IntegerProperty(verbose_name=u'Рейтинг')
    status = ndb.IntegerProperty(verbose_name=u'Статус')
    is_public = ndb.BooleanProperty(
        verbose_name=u'Показывать на сайте?',
        default=True)

    material = ndb.StringProperty(verbose_name=u'Материал', default='', indexed=False)
    size = ndb.StringProperty(verbose_name=u'Размер', default='', indexed=False)
    weight = ndb.StringProperty(verbose_name=u'Вес', default='', indexed=False)

    box_material = ndb.StringProperty(verbose_name=u'Материал/тип упаковки', default='', indexed=False)
    box_size = ndb.StringProperty(verbose_name=u'Размер упаковки', default='', indexed=False)
    box_weight = ndb.StringProperty(verbose_name=u'Вес упаковки', default='', indexed=False)
    box_amount = ndb.StringProperty(verbose_name=u'Количество в упаковке', default='', indexed=False)

    price_retail = ndb.FloatProperty(verbose_name=u'Цена (розничная)')
    price_trade = ndb.FloatProperty(verbose_name=u'Цена (оптовая)')

    leftovers = ndb.IntegerProperty(verbose_name=u'Остаток на складе')
    leftovers_on_way = ndb.IntegerProperty(verbose_name=u'Остаток в пути')
    receipt_date = ndb.DateProperty(verbose_name=u'Дата поступления')

    badge = ndb.StringProperty(verbose_name=u'Бэйдж', indexed=False)
    description = ndb.TextProperty(verbose_name=u'Описание', default='')

    images_list = ndb.StructuredProperty(ProductImage, repeated=True)

    _PROPERTIES = Base._PROPERTIES.union([
        'id_1c',
        'catalogue_id',
        'barcode',
        'name',
        'category',
        'genre',
        'series',
        'brand',
        'country',
        'rating',
        'status',
        'is_public',
        'material',
        'size',
        'weight',
        'box_material',
        'box_size',
        'box_weight',
        'box_amount,'
        'price_retail',
        'price_trade',
        'leftovers',
        'leftovers_on_way',
        'receipt_date',
        'description',
        'images'
    ])

    @cached_property
    def url(self):
        return url_for('product.get_product', key_id=self.key.id())

    @property
    def images(self):
        return [img.url for img in self.images_list]

    @ndb.toplevel
    def clear_sections(self):
        try:
            key_id = self.key.id()
        except:
            return False
        flag = False
        category = Category.get_exist(self.category)
        if _clear_section(category, key_id):
            category.put_async()
            flag = True
        genre = Genre.get_exist(self.genre)
        if _clear_section(genre, key_id):
            genre.put_async()
            flag = True
        series = Series.get_exist(self.series)
        if _clear_section(series, key_id):
            series.put_async()
            flag = True
        brand = Brand.get_exist(self.brand)
        if _clear_section(brand, key_id):
            brand.put_async()
            flag = True
        return flag

    def set_sections(self):
        try:
            key_id = self.key.id()
        except:
            return False
        flag = False
        if self.category:
            category = Category.new_or_exist(self.category)
            if _set_section(category, key_id, self.is_public):
                category.put()
                flag = True
        if self.genre:
            genre = Genre.new_or_exist(self.genre)
            if _set_section(genre, key_id, self.is_public):
                genre.put()
                flag = True
        if self.series:
            series = Series.new_or_exist(self.series)
            if _set_section(series, key_id, self.is_public):
                series.put()
                flag = True
        if self.brand:
            brand = Brand.new_or_exist(self.brand)
            if _set_section(brand, key_id, self.is_public):
                brand.put()
                flag = True
        return flag

    def _pre_put_hook(self):
        self.category = strip_string(self.category)
        self.genre = strip_string(self.genre)
        self.series = strip_string(self.series)
        self.badge = strip_string(self.badge)
        self.barcode = strip_string(self.barcode)
        self.brand = strip_string(self.brand)
        self.country = strip_string(self.country)
        self.material = strip_string(self.material)

    def _post_put_hook(self, future):
        self.set_sections()

    @classmethod
    def _pre_delete_hook(cls, key):
        p = key.get()
        if p:
            p.clear_sections()
            for img in p.images_list:
                img.delete_blob()

