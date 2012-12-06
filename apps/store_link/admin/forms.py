# -*- coding: utf-8 -*-
from flaskext import wtf

class StoreLinkForm(wtf.Form):
    name = wtf.TextField(
        u'Название магазина',
        description=u'Введите название магазина',
        validators=[wtf.validators.required()]
    )
    link = wtf.TextField(
        u'Ссылка на магазин',
        description=u'Укажите ссылку на магазин. Ссылка должна быть вида http://example.ru',
        validators=[wtf.validators.required(), wtf.validators.url()]
    )
    description = wtf.TextField(
        u'Описание',
        description=u'Введите краткое описание магазина'
    )
