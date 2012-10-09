# -*- coding: utf-8 -*-

from flaskext import wtf

class ContactForm(wtf.Form):
    order_id = wtf.IntegerField(
        u'Порядок сортировки',
        description=u'От большего к меньшему',
        default=0
    )

    is_public = wtf.BooleanField(
        u'Показывать на сайте?',
        description=u'Показывать ли данный контакт на страницах сайта?',
        default=False
    )

    title = wtf.TextField(
        u'Название',
        description=u'Например, "Головной офис" или "Склад"'
    )

    zip_code = wtf.TextField(
        u'Почтовый индекс',
        description=u'Введите почтовый индекс'
    )
    city = wtf.TextField(
        u'Город',
        description=u'Введите город'
    )
    address = wtf.TextAreaField(
        u'Адрес',
        description=u'Введите полный адрес'
    )
    telephones = wtf.TextAreaField(
        u'Телефоны',
        description=u'Введите телефоны'
    )
    faxes = wtf.TextAreaField(
        u'Факсы',
        description=u'Введите факсы'
    )
    additional_info = wtf.TextAreaField(
        u'Дополнительная информация',
        description=u'Введите любую другую информацию'
    )

    latitude = wtf.FloatField(
        u'Широта',
        description=u'Введите широту на карте',
        default=0.0
    )

    longitude =wtf.FloatField(
        u'Долгота',
        description=u'Введите долготу на карте',
        default=0.0
    )