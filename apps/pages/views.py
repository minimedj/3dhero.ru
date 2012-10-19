# -*- coding: utf-8 -*-
import flask
from apps.blog.models import Post
from apps.product.models import Product, Series, Brand
from apps.utils.paginator import Paginator, EmptyPage, InvalidPage
from apps.contact.models import Contact
from apps.manager.models import Manager

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
    series = Series.query(
                Series.is_public == True,
                Series.is_products == True
            ).order(Series.name)
    series_count = series.count()
    brands_count = Brand.query(Brand.is_public == True).count()
    return flask.render_template(
        'pages/index.html',
        posts=posts,
        products=products,
        product_count=product_count,
        series=series,
        series_count= series_count,
        brands_count=brands_count
    )

@mod.route('/catalogue/', defaults={'page':1})
@mod.route('/catalogue/page/<int:page>/')
def catalogue(page):
    products = Product.query(
        Product.is_public == True,
        Product.images_list.is_image == True).order(-Product.rating)
    products = get_paginator(products, page)
    return flask.render_template(
        'pages/catalogue.html',
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