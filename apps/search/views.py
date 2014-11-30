# -*- coding: utf-8 -*-
from google.appengine.ext import ndb
from flask import Blueprint, redirect, render_template, url_for, session

from apps.search.forms import SearchForm
from apps.pages.views import get_paginator, PRODUCT_VIEW_TYPES
from apps.product.models import Product, Category
import util


mod = Blueprint(
    'search',
    __name__,
    url_prefix='/search',
    template_folder='templates'
)


@mod.route('/', methods=['POST'])
def index_form():
    form = SearchForm(csrf_enabled=False)
    if form.validate_on_submit():
        query = form.query.data.lower()
        return redirect(url_for('search.index', query=query))
    return redirect(util.get_next_url())


@util.memcached()
def search_categories(query):
    categories_q = Category.query().fetch(projection=[Category.name])
    categories_keys = [
        c.key for c in categories_q if query in c.name.lower()
    ]
    if categories_keys:
        return ndb.get_multi(categories_keys)
    return []


@util.memcached()
def get_searchable_products():
    products_q = Product.query()
    return products_q.fetch(
        projection=[Product.name, Product.barcode, Product.catalogue_id]
    )


@util.memcached()
def search_products(query):
    products_q = get_searchable_products()
    ids = []
    for product in products_q:
        if query in product.name.lower() \
                or query in product.barcode \
                or query in product.catalogue_id:
            ids.append(product.key)
    if ids:
        return ndb.get_multi(ids)
    return []


def search_products_paginator(products, page):
    return get_paginator(products, page, product_per_page=20)


@mod.route('/<string:query>/', defaults={'page': 1})
@mod.route('/<string:query>/page/<int:page>/')
def index(query, page):
    view_type = util.param('product_view_type', int)
    session_view_type = session.get('product_view_type', None)
    if session_view_type is None or\
            session_view_type not in PRODUCT_VIEW_TYPES.itervalues():
        if view_type in PRODUCT_VIEW_TYPES.itervalues():
            session['product_view_type'] = view_type
        else:
            session['product_view_type'] = PRODUCT_VIEW_TYPES['tile']
    else:
        if view_type in PRODUCT_VIEW_TYPES.itervalues():
            session['product_view_type'] = view_type

    query = query.strip().lower()
    if not query:
        return render_template(
            'search/index.html',
            title=u"Поиск по сайту",
            query=query,
            categories=[],
            products=[]
        )
    products = search_products(query)
    if products:
        products = search_products_paginator(products, page)
    return render_template(
        'search/index.html',
        title=u'Поиск по сайту',
        query=query,
        categories=search_categories(query),
        products=products
    )
