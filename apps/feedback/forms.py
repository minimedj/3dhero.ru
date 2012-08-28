# -*- coding: utf-8 -*-
from flaskext import wtf

class FeedbackForm(wtf.Form):
    subject = wtf.TextField(u'Тема', [wtf.validators.required()])
    feedback = wtf.TextAreaField(u'Вопрос/предложение', [wtf.validators.required()])
    email = wtf.TextField(u'Email (необязательно)', [
        wtf.validators.optional(),
        wtf.validators.email(
            u"Хмм... это не выглядит похожим на настоящий email,\
            вероятнее всего Вы ошиблись"),
        ])