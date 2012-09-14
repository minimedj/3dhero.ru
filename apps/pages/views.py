# -*- coding: utf-8 -*-
import flask
from apps.product.models import Product
from apps.utils.paginator import Paginator, EmptyPage, InvalidPage


mod = flask.Blueprint(
    "pages",
    __name__,
    template_folder='templates'
)

PRODUCT_PER_PAGE = 16

@mod.route('/', defaults={'page':1})
@mod.route('/page/<int:page>/')
def index(page):
    products = Product.query(
        Product.is_public == True,
        Product.images_list.is_image == True).order(-Product.rating)
    paginator = Paginator(products, PRODUCT_PER_PAGE)
    try:
        products = paginator.page(page)
    except (EmptyPage, InvalidPage):
        products = paginator.page(paginator.num_pages())
    return flask.render_template(
        'pages/index.html',
        html_class='welcome',
        channel_name='welcome',
        products=products
    )


_blueprints = (mod,)