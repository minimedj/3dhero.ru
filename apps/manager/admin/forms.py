# -*- coding: utf-8 -*-

from flaskext import wtf


class ManagerForm(wtf.Form):
    name = wtf.TextField(
        u'Имя',
        description=u'Введите имя, это поле обязательно для заполнения',
        validators=[wtf.validators.required()]
    )
    position = wtf.TextField(
        u'Должность'
    )
    email = wtf.TextField(
        u'Email',
        description=u'Введите Email, это поле обязательно для заполнения',
        validators=[
            wtf.validators.email(u'Это не похоже на Email'),
            wtf.validators.required()
        ]
    )
    telephone = wtf.TextField(
        u'Телефон'
    )
    fax = wtf.TextField(
        u'Факс'
    )
    mobile = wtf.TextField(
        u'Мобильный'
    )
    icq = wtf.TextField(
        u'ICQ'
    )
    skype = wtf.TextField(
        u'Skype'
    )
    is_public = wtf.BooleanField(
        u'Показывать в "Контактах"?',
        description=u'Показывать мененджера на страницах сайта?'
    )
    is_mailable = wtf.BooleanField(
        u'Доставлять почту?',
        description=u'Отправлять мененджеру уведомления и рассылки?'
    )
