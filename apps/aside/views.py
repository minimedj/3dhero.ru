# -*- coding: utf-8 -*-
from flask import render_template

import auth
from apps.product.models import Category
from pytils import dt


def get_aside(active='category', key_id=None):
    sections=[]
    if active == 'category':
        if auth.is_admin():
          sections = Category.query().order(Category.name)
        else:
            sections = Category.query(
                Category.is_public == True
            ).order(Category.name)
            sections = [s for s in sections if s.public_product_count]

    if key_id:
        key_id = int(key_id)
    return render_template(
        'aside.html',
        active=active,
        sections=sections,
        key_id=key_id
    )


def get_str_property(name, value, itemprop=None):
    return render_template(
        'str_property.html',
        name=name, value=value, itemprop=itemprop
    )


def date_str(d):
    return dt.ru_strftime(u"%d %B %Y в %H:%M", d, inflected=True)