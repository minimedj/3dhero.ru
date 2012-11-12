# -*- coding: utf-8 -*-

from flaskext import wtf

class PriceFileForm(wtf.Form):
    order_id = wtf.IntegerField(
        u'Порядок сортировки',
        description=u'Укажите порядок сортировки. '
                    u'Сортируется от большего к меньшему.',
        default=0,
        validators=[wtf.validators.optional()]
    )
    attach_file_ = wtf.FileField(
        u'Файл',
        description=u'Выберите файл для загрузки',
        validators=[wtf.validators.optional()]
    )
    description = wtf.TextAreaField(
        u'Описание',
        description=u'Введите краткое описание для файла',
        validators=[wtf.validators.optional()]
    )