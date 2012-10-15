# -*- coding: utf-8 -*-

from flaskext import wtf

class OrderForm(wtf.Form):
    count = wtf.IntegerField(
        u'Количество',
        description=u'Введите количество товара для заказа.',
        default=1,
        validators=[
            wtf.validators.required(message=u'Введите число большее 0'),
            wtf.validators.number_range(
                min=1,
                message=u'Число должно быть положительным'
            )]
    )