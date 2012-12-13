# -*- coding: utf-8 -*-

from flaskext import wtf

class SearchForm(wtf.Form):
    query = wtf.TextField(validators=[wtf.validators.required()])
