# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, render_template, request, url_for, session
from apps.search.forms import SearchForm
from auth import is_admin
from apps.product.models import Product, Category
from util import get_next_url, param
from google.appengine.ext import ndb
from google.appengine.api import memcache
from apps.pages.views import get_paginator, PRODUCT_VIEW_TYPES


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
    return redirect(get_next_url())

@mod.route('/<string:query>/', defaults={'page': 1})
@mod.route('/<string:query>/page/<int:page>/')
def index(query, page):
    view_type = param('product_view_type', int)
    session_view_type = session.get('product_view_type', None)
    if session_view_type is None or session_view_type not in PRODUCT_VIEW_TYPES.itervalues():
        if view_type in PRODUCT_VIEW_TYPES.itervalues():
            session['product_view_type'] = view_type
        else:
            session['product_view_type'] = PRODUCT_VIEW_TYPES['tile']
    else:
        if view_type in PRODUCT_VIEW_TYPES.itervalues():
            session['product_view_type'] = view_type

    products = []
    categories = []
    query = query.strip().lower()
    if not query:
        return render_template(
            'search/index.html',
            title=u"Поиск по сайту",
            query=query,
            categories=categories,
            products=products
        )
    categories_q = Category.query().fetch(projection=[Category.name])
    cids = memcache.get('search_cids-%s' % query)
    if not cids:
        cids = []
        for category in categories_q:
            if query in category.name.lower():
              cids.append(category.key)
        memcache.add('search_cids-%s' % query, cids, 600)
    if cids:
        categories = ndb.get_multi(cids)
    if is_admin():
        products_q = Product.query()
    else:
        products_q = Product.query(Product.is_available == True)
    products_q = products_q.fetch(
        projection=[Product.name, Product.barcode, Product.catalogue_id]
    )
    ids = memcache.get('search_ids-%s' % query)
    if not ids:
        ids = []
        for product in products_q:
            if query in product.name.lower()\
                    or query in product.barcode\
                    or query in product.catalogue_id:
                ids.append(product.key)
        memcache.add('search_ids-%s' % query, ids, 600)
    if ids:
        products = ndb.get_multi(ids)
        products = get_paginator(products, page, product_per_page=20)
    return render_template(
        'search/index.html',
        title=u'Поиск по сайту',
        query=query,
        categories=categories,
        products=products
    )
