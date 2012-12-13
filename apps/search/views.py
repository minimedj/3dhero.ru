# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, render_template
from apps.search.forms import SearchForm
from auth import is_admin
from apps.product.models import Product
from util import get_next_url
from google.appengine.ext import ndb


mod = Blueprint(
    'search',
    __name__,
    url_prefix='/search',
    template_folder='templates'
)


@mod.route('/', methods=['POST'])
def index():
    form = SearchForm(csrf_enabled=False)
    next_url = get_next_url()
    if form.validate_on_submit():
        query = form.query.data.lower()
        if is_admin():
            products_q = Product.query()
        else:
            products_q = Product.query(Product.is_available == True)
        products_q = products_q.fetch(projection=[Product.name])
        ids = []
        for product in products_q:
            if query in product.name.lower():
                ids.append(product.key)
        if ids:
            products = ndb.get_multi(ids)
        else:
            products = []
        return render_template(
            'search/index.html',
            query=query,
            products=products
        )
    return redirect(next_url)