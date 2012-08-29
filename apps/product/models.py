# -*- coding: utf-8 -*-
from google.appengine.ext import ndb
from mgi.models import Base

class BaseSection(Base):
    name = ndb.StringProperty(verbose_name=u'Название')
    name_lowercase = ndb.ComputedProperty(lambda self: self.name.lower())
    products = ndb.IntegerProperty(repeated=True)
    hide_products = ndb.IntegerProperty(repeated=True)
    is_public = ndb.BooleanProperty(verbose_name=u'Показывать на сайте?')

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
        if key_id in is_exist.products:
            is_exist.products.remove(key_id)
            is_exist.put()


class Category(BaseSection):
    pass

class Genre(BaseSection):
    pass

class Series(BaseSection):
    pass


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
    if section:
        if is_public:
            if key_id in section.hide_products:
                section.hide_products.remove(key_id)
                if key_id not in section.products:
                    section.products.append(key_id)
                    return True
                else:
                    return False
        else:
            if key_id in section.products:
                section.products.remove(key_id)
                if key_id not in section.hide_products:
                    section.hide_products.append(key_id)
                    return True
                else:
                    return False
    return False

class Product(Base):
    id_1c = ndb.StringProperty(verbose_name=u'Код 1С')
    catalogue_id = ndb.StringProperty(verbose_name=u'Артикул')
    barcode = ndb.StringProperty(verbose_name=u'Штрих код')

    name = ndb.StringProperty(verbose_name=u'Название')
    category = ndb.StringProperty(verbose_name=u'Категория')
    genre = ndb.StringProperty(verbose_name=u'Жанр')
    series = ndb.StringProperty(verbose_name=u'Серия')

    brand = ndb.StringProperty(verbose_name=u'Брэнд/Производитель')
    country = ndb.StringProperty(verbose_name=u'Страна')

    rating = ndb.IntegerProperty(verbose_name=u'Рейтинг')
    status = ndb.IntegerProperty(verbose_name=u'Статус')
    is_public = ndb.BooleanProperty(
        verbose_name=u'Показывать на сайте?',
        default=True)

    material = ndb.StringProperty(verbose_name=u'Материал')
    size = ndb.StringProperty(verbose_name=u'Размер')
    weight = ndb.StringProperty(verbose_name=u'Вес')

    box_material = ndb.StringProperty(verbose_name=u'Материал/тип упаковки')
    box_size = ndb.StringProperty(verbose_name=u'Размер упаковки')
    box_weight = ndb.StringProperty(verbose_name=u'Вес упаковки')

    price_retail = ndb.FloatProperty(verbose_name=u'Цена (розничная)')
    price_trade = ndb.FloatProperty(verbose_name=u'Цена (оптовая)')

    leftovers = ndb.IntegerProperty(verbose_name=u'Остаток на складе')
    leftovers_on_way = ndb.IntegerProperty(verbose_name=u'Остаток в пути')
    receipt_date = ndb.DateProperty(verbose_name=u'дата поступления')

    badge = ndb.StringProperty(u'Бэйдж')
    description = ndb.StringProperty(u'Описание')

    @ndb.toplevel
    def clear_sections(self):
        try:
            key_id = self.key.id()
        except:
            return False
        flag = False
        category = Category.get_exist(self.category)
        if _clear_section(category, key_id):
            category.async_put()
            flag = True
        genre = Genre.get_exist(self.genre)
        if _clear_section(genre, key_id):
            genre.async_put()
            flag = True
        series = Series.get_exist(self.series)
        if _clear_section(series, key_id):
            series.async_put()
            flag = True
        return flag

    @ndb.toplevel
    def set_sections(self):
        try:
            key_id = self.key.id()
        except:
            return False
        flag = False
        category = Category.get_exist(self.category)
        if _set_section(category, key_id, self.is_public):
            category.async_put()
            flag = True
        genre = Genre.get_exist(self.genre)
        if _set_section(genre, key_id, self.is_public):
            genre.async_put()
            flag = True
        series = Series.get_exist(self.series)
        if _set_section(series, key_id, self.is_public):
            series.async_put()
            flag = True
        return flag

    def _pre_put_hook(self):
        self.clear_sections()

    def _post_put_hook(self, future):
        self.set_sections()

    @classmethod
    def _pre_delete_hook(cls, key):
        p = cls.get(key)
        if p:
            p.clear_sections()

