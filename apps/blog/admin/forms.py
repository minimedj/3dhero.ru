# -*- coding: utf-8 -*-

from flaskext import wtf

class PostForm(wtf.Form):
    title = wtf.TextField(
        u'Заголовок',
        description=u'Введите заголовк записи',
        validators=[wtf.validators.required()]
    )
    is_public = wtf.BooleanField(
        u'Публичная?',
        description=u'Отметьте, чтобы показывать новость на сайте',
        default=False,
        validators=[wtf.validators.optional()]
    )
    short_text = wtf.TextField(
        u'Краткое описание',
        description=u'Введите краткое описание',
        validators=[wtf.validators.required()]
    )
    text = wtf.TextField(
        u'Текст',
        description=u'Введите основной текст записи',
        validators=[wtf.validators.optional()]
    )