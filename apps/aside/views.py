# -*- coding: utf-8 -*-
from flask import render_template
from apps.product.models import Series

def get_aside(active='series', key_id=None):
    active = 'series'
    sections=[]
    if active == 'series':
        sections = Series.query(
            Series.is_public == True,
            Series.is_products == True
        ).order(Series.name)
    if key_id:
        key_id = int(key_id)
    return render_template(
        'aside.html',
        active=active,
        sections = sections,
        key_id=key_id
    )

def get_str_property(name, value):
    return render_template(
        'str_property.html',
        name=name, value=value
    )