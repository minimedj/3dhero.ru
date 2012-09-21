# -*- coding: utf-8 -*-
import flask
from apps.product.models import Product, Series
from apps.utils.paginator import Paginator, EmptyPage, InvalidPage

mod = flask.Blueprint(
    "pages",
    __name__,
    template_folder='templates'
)

PRODUCT_PER_PAGE = 18

def get_paginator(products, page):
    paginator = Paginator(products, PRODUCT_PER_PAGE)
    try:
        products = paginator.page(page)
    except (EmptyPage, InvalidPage):
        products = paginator.page(paginator.num_pages())
    return products

@mod.route('/', defaults={'page':1})
@mod.route('/page/<int:page>/')
def index(page):
    products = Product.query(
        Product.is_public == True,
        Product.images_list.is_image == True).order(-Product.rating)
    products = get_paginator(products, page)
    return flask.render_template(
        'pages/index.html',
        html_class='welcome',
        channel_name='welcome',
        products=products
    )

@mod.route('/s/<key_id>/', defaults={'page':1})
@mod.route('/s/<int:key_id>/page/<int:page>/')
def series(key_id, page):
    series = Series.retrieve_by_id(key_id)
    if not series:
        return flask.redirect(flask.url_for(
            'pages.index'
        ))
    products_ids = series.products
    products = [Product.get_by_id(p) for p in products_ids]
    products = get_paginator(products, page)
    return flask.render_template(
        'pages/series.html',
        series=series,
        products=products,
        key_id=key_id
    )



_blueprints = (mod,)