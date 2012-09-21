# -*- coding: utf-8 -*-
from flask import Blueprint, url_for, redirect, render_template
from apps.product.models import Product
from util import get_next_url

mod = Blueprint(
    'product',
    __name__,
    url_prefix='/product',
    template_folder='templates'
)

@mod.route('/<int:key_id>/', methods=['GET'])
def get_product(key_id):
    product = Product.retrieve_by_id(key_id)
    back_url = get_next_url()
    if not product:
        return redirect(url_for('pages.index'))
    return render_template(
        'product/get.html',
        product=product,
        back_url=back_url
    )

_blueprints = (mod,)
