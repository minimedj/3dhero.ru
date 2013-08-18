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
from auth import is_admin
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

SITEMAP_XML_TIMEOUT = 60*60*48


def get_paginator(products, page, product_per_page = 18):
    paginator = Paginator(products, product_per_page)
    try:
        products = paginator.page(page)
    except (EmptyPage, InvalidPage):
        products = paginator.page(paginator.num_pages)
    return products


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


def categories_stat():
    categories_obj = Category.query(Category.is_public == True).order(
        Category.name
    )
    categories = []
    for c in categories_obj:
        if c.public_product_count:
            categories.append(c)
    categories_count = len(categories)
    if categories_count:
        categories_count = pytils.numeral.get_plural(
            categories_count,
            (u'категории', u'категорий', u'категорий')
        )
    return categories, categories_count


def product_stat():
    product_count = Product.query(Product.is_available == True).count()
    if product_count:
        product_count = pytils.numeral.get_plural(
            product_count,
            (u"позиции", u"позиций", u"позиций")
        )
    return product_count


def countries_stat():
    countries_count = Country.query(Country.is_public == True).count()
    if countries_count:
        countries_count = pytils.numeral.get_plural(
            countries_count,
            (u'страны', u'стран', u'стран')
        )
    return countries_count


@mod.route('/')
def index():
    posts = Post.query(Post.is_public == True).order(-Post.created)
    posts_count = posts.count()
    posts = posts.fetch(4)
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
    if is_admin():
        products = Product.query().order(-Product.rating)
    else:
        products = Product.query()\
            .order(-Product.rating)\
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
    if is_admin():
        products = Product.query().order(-Product.created)
    else:
        products = Product.query(
            Product.is_public == True).order(-Product.created)
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
    category = Category.retrieve_by_id(key_id)
    if not category:
        return flask.redirect(flask.url_for(
            'pages.index'
        ))
    products = Product\
        .query(Product.category == category.name)\
        .order(-Product.is_available)\
        .order(-Product.leftovers_on_way)\
        .order(-Product.leftovers)
    products = get_paginator(products, page)
    return flask.render_template(
        'pages/category.html',
        title=u'{} "{}"'.format(u'Категория', category.name),
        category=category,
        products=products,
        key_id=key_id
    )


@mod.route('/contact/')
def contacts():
    contacts = Contact.query(Contact.is_public == True).order(-Contact.order_id)
    managers = Manager.query(Manager.is_public == True)
    return flask.render_template(
        'pages/contact.html',
        title=u'Контакты',
        contacts=contacts,
        managers=managers
    )

@mod.route('/sitemap.xml')
def sitemap_xml():
    products = memcache.get('sitemap_xml')
    if not products:
        products = Product.query().fetch(projection=[Product.name])
        memcache.add('sitemap_xml', products, SITEMAP_XML_TIMEOUT)
    categories = memcache.get('sitemap_xml_categories')
    if not categories:
        categories = Category.query().fetch(projection=[Category.name])
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
