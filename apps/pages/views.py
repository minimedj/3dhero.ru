# -*- coding: utf-8 -*-
import flask
from google.appengine.ext import ndb
from apps.blog.models import Post
from apps.product.models import Product, Category, Brand, Country
from apps.product.models import CategoryProduct
from apps.utils.paginator import Paginator, EmptyPage, InvalidPage
from apps.contact.models import Contact
from apps.manager.models import Manager
import util

PRODUCT_VIEW_TYPES = {
    'tile': 1,
    'icon': 2,
    'table': 3
}

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
        products = paginator.page(paginator.num_pages)
    return products

@mod.route('/')
def index():
    posts = Post.query(Post.is_public == True).order(-Post.created).fetch(5)
    products = Product.query(Product.is_available == True).order(-Product.created).fetch(6)
    product_count = Product.query(Product.is_available == True).count()
    categories_obj = Category.query(Category.is_public == True).order(Category.name)
    categories = []
    for c in categories_obj:
        if c.public_product_count:
            categories.append(c)
    categories_count = len(categories)
    countries_count = Country.query(Country.is_public == True).count()
    brands_objs = Brand.query(Brand.is_public == True)
    brands_count = 0
    for b in brands_objs:
        if b.public_product_count:
            brands_count += 1
    return flask.render_template(
        'pages/index.html',
        posts=posts,
        products=products,
        product_count=product_count,
        categories=categories,
        categories_count= categories_count,
        countries_count=countries_count,
        brands_count=brands_count
    )

@mod.route('/catalogue/', defaults={'page':1})
@mod.route('/catalogue/page/<int:page>/')
def catalogue(page):
    products = Product.query(
        Product.is_public == True).order(-Product.rating)
    products = get_paginator(products, page)
    return flask.render_template(
        'pages/catalogue.html',
        products=products
    )

@mod.route('/c/<key_id>/', defaults={'page':1})
@mod.route('/c/<int:key_id>/page/<int:page>/')
def category(key_id, page):
    view_type = util.param('product_view_type', int)
    session_view_type = flask.session.get('product_view_type', None)
    if session_view_type is None or session_view_type not in PRODUCT_VIEW_TYPES.itervalues():
        if view_type in PRODUCT_VIEW_TYPES.itervalues():
            flask.session['product_view_type'] = view_type
        else:
            flask.session['product_view_type'] = PRODUCT_VIEW_TYPES['tile']
    else:
        if view_type in PRODUCT_VIEW_TYPES.itervalues():
            flask.session['product_view_type'] = view_type
    category = Category.retrieve_by_id(key_id)
    if not category:
        return flask.redirect(flask.url_for(
            'pages.index'
        ))
    category_products = CategoryProduct.query(
        CategoryProduct.section_key==category.key,
        CategoryProduct.is_public==True
    )
    products = ndb.get_multi([p.product_key for p in category_products])
    products = get_paginator(products, page)
    return flask.render_template(
        'pages/category.html',
        category=category,
        products=products,
        key_id=key_id
    )


@mod.route('/contact/')
def contacts():
    contacts = Contact.query(Contact.is_public==True).order(-Contact.order_id)
    managers = Manager.query(Manager.is_public==True)
    return flask.render_template(
        'pages/contact.html',
        contacts=contacts,
        managers=managers
    )

_blueprints = (mod,)