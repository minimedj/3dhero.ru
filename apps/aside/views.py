# -*- coding: utf-8 -*-
from flask import render_template
from apps.product.models import Category

def get_aside(active='category', key_id=None):
    sections=[]
    if active == 'category':
        sections = Category.query(
            Category.is_public == True
        ).order(Category.name)
    if key_id:
        key_id = int(key_id)
    return render_template(
        'aside.html',
        active=active,
        sections = sections,
        key_id=key_id
    )

def get_str_property(name, value, itemprop=None):
    return render_template(
        'str_property.html',
        name=name, value=value, itemprop=itemprop
    )