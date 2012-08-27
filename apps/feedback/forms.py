# -*- coding: utf-8 -*-
from flaskext import wtf

class FeedbackForm(wtf.Form):
    subject = wtf.TextField('Subject', [wtf.validators.required()])
    feedback = wtf.TextAreaField('Feedback', [wtf.validators.required()])
    email = wtf.TextField('Email (optional)', [
        wtf.validators.optional(),
        wtf.validators.email("That doesn't look like an email"),
        ])