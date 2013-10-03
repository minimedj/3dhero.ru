# -*- coding: utf-8 -*-
from flaskext import wtf
from wtfrecaptcha.fields import RecaptchaField


class FeedbackForm(wtf.Form):
    subject = wtf.TextField(u'Тема', [wtf.validators.required()])
    feedback = wtf.TextAreaField(u'Вопрос/предложение', [wtf.validators.required()])
    email = wtf.TextField(u'Email (необязательно)', [
        wtf.validators.optional(),
        wtf.validators.email(
            u"Хмм... это не выглядит похожим на настоящий email,\
            вероятнее всего Вы ошиблись"),
        ])


class FeedbackCaptchaForm(FeedbackForm):
    def __init__(self, public_key=None, private_key=None, *args, **kwargs):
        super(FeedbackCaptchaForm, self).__init__(*args, **kwargs)
        self.public_key = public_key
        self.private_key = private_key

    captcha = RecaptchaField(
      u'Введите указанный текст',
      secure=True
    )