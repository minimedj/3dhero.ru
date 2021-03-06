# -*- coding: utf-8 -*-
import flask
from google.appengine.api import memcache
from apps.blog.models import Post
from apps.product.models import Product, Category, Brand, Country
from apps.utils.paginator import Paginator, EmptyPage, InvalidPage
from apps.contact.models import Contact
from apps.manager.models import Manager
from apps.store_link.models import StoreLink
import util
import pytils


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

SITEMAP_XML_TIMEOUT = 60 * 60 * 24


def get_paginator(products, page, product_per_page=21):
    paginator = Paginator(products, product_per_page)
    try:
        products = paginator.page(page)
    except (EmptyPage, InvalidPage):
        products = paginator.page(paginator.num_pages)
    return products


@util.memcached()
def brands_stat():
    brands_obj = Brand.query(Brand.is_public == True).order(
        Brand.name
    )
    brands = []
    for b in brands_obj:
        if b.public_product_count:
            brands.append(b)
    brands_count = len(brands)
    if brands_count:
        brands_count = pytils.numeral.get_plural(
            brands_count,
            (u'бренда и производителя',
             u'брендов и производителей',
             u'брендов и производителей')
        )
    return brands, brands_count


@util.memcached()
def categories_stat():
    categories_obj = list(Category.query().order(Category.name))
    categories = []
    for c in categories_obj:
        if c.products_count:
            categories.append(c)
    categories_count = len(categories)

    if categories_count:
        categories_count = pytils.numeral.get_plural(
            categories_count,
            (u'категории', u'категорий', u'категорий')
        )
    return categories, categories_count


@util.memcached()
def product_stat():
    product_count = Product.query().count()
    if product_count:
        product_count = pytils.numeral.get_plural(
            product_count,
            (u"позиции", u"позиций", u"позиций")
        )
    return product_count


@util.memcached()
def countries_stat():
    countries_obj = Country.query()
    countries = []
    for c in countries_obj:
      if c.products_count:
          countries.append(c)
    countries_count = len(countries)
    if countries_count:
        countries_count = pytils.numeral.get_plural(
            countries_count,
            (u'страны', u'стран', u'стран')
        )
    return countries_count


@util.memcached()
def get_latest_posts():
    posts_objs = Post.query(Post.is_public == True).order(-Post.created)
    posts_count = posts_objs.count()
    posts_objs = posts_objs.fetch(4)
    return posts_objs, posts_count


@mod.route('/')
def index():
    posts, posts_count = get_latest_posts()
    brands, brands_count = brands_stat()
    categories, categories_count = categories_stat()
    product_count = product_stat()
    countries_count = countries_stat()
    store_links = StoreLink.query()
    return flask.render_template(
        'pages/index.html',
        posts=posts,
        posts_count=posts_count,
        product_count=product_count,
        categories=categories,
        categories_count=categories_count,
        countries_count=countries_count,
        brands_count=brands_count,
        brands=brands,
        store_links=store_links
    )


@mod.route('/catalogue/', defaults={'page': 1})
@mod.route('/catalogue/page/<int:page>/')
def catalogue(page):
    products = Product.query() \
        .order(-Product.rating) \
        .order(-Product.leftovers_on_way) \
        .order(-Product.leftovers)
    products = get_paginator(products, page)
    return flask.render_template(
        'pages/catalogue.html',
        title=u'Каталог товаров',
        products=products
    )


@mod.route('/c/li/', defaults={'page': 1})
@mod.route('/c/li/page/<int:page>/')
def last_incoming(page):
    products = Product.query().order(-Product.created)
    products = get_paginator(products, page)
    return flask.render_template(
        'pages/last_incoming.html',
        title=u'Последние поступления',
        products=products
    )


@mod.route('/c/<key_id>/', defaults={'page': 1})
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
    category_obj = Category.retrieve_by_id(key_id)
    if not category_obj:
        return flask.redirect(flask.url_for(
            'pages.index'
        ))
    products = Product\
        .query(Product.category == category_obj.name)\
        .order(-Product.leftovers_on_way)\
        .order(-Product.leftovers)
    products = get_paginator(products, page)
    return flask.render_template(
        'pages/category.html',
        title=u'{} "{}"'.format(u'Категория', category_obj.name),
        category=category_obj,
        products=products,
        key_id=key_id
    )


@mod.route('/contact/')
def contacts():
    contacts_obj = Contact.query(Contact.is_public == True).order(-Contact.order_id)
    managers = Manager.query(Manager.is_public == True)
    return flask.render_template(
        'pages/contact.html',
        title=u'Контакты',
        contacts=contacts_obj,
        managers=managers
    )


@mod.route('/sitemap.xml')
def sitemap_xml():
    products = memcache.get('sitemap_xml')
    if not products:
        products = Product.query().fetch(keys_only=True)
        memcache.add('sitemap_xml', products, SITEMAP_XML_TIMEOUT)
    categories = memcache.get('sitemap_xml_categories')
    if not categories:
        categories = Category.query().fetch(keys_only=True)
        memcache.add('sitemap_xml_categories', categories, SITEMAP_XML_TIMEOUT)
    response = flask.make_response(
        flask.render_template(
            'pages/sitemap.xml',
            products=products,
            categories=categories)
    )
    response.headers['Content-Type'] = 'text/xml; charset=utf-8'
    return response

_blueprints = (mod,)
