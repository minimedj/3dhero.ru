# -*- coding: utf-8 -*-

from flask.ext import wtf
from apps.product.models import Category, Series

class CategoryForm(wtf.Form):
    name = wtf.TextField(
        u'Название',
        description=u'Введите назнание категории',
        validators=[wtf.validators.required()]
    )
    is_public = wtf.BooleanField(
        u'Публичная?',
        description=u'Показывать категорию на сайте?',
        validators=[wtf.validators.optional()]
    )

    def validate(self, is_edit=False):
        rv = wtf.Form.validate(self)
        if not rv:
            return False
        name = self.name.data.lower()
        check_cat = Category.query(Category.name_lowercase == name).count()
        if check_cat and not is_edit:
            self.name.errors.append(u'Название категории должно быть уникальным')
            return False
        return True


class SeriesForm(wtf.Form):
    name = wtf.TextField(
        u'Название',
        description=u'Введите назнание серии',
        validators=[wtf.validators.required()]
    )
    is_public = wtf.BooleanField(
        u'Публичная?',
        description=u'Показывать серию на сайте?',
        validators=[wtf.validators.optional()]
    )

    def validate(self, is_edit=False):
        rv = wtf.Form.validate(self)
        if not rv:
            return False
        name = self.name.data.lower()
        check_cat = Series.query(Series.name_lowercase == name).count()
        if check_cat and not is_edit:
            self.name.errors.append(u'Название серии должно быть уникальным')
            return False
        return True