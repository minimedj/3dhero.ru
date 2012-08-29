# -*- coding: utf-8 -*-
from flask import Blueprint, url_for, redirect, render_template
from apps.product.models import Product

mod = Blueprint(
    'product',
    __name__,
    url_prefix='/product',
    template_folder='templates'
)

@mod.route('/<int:key_id>/', methods=['GET'])
def get_product(key_id):
    product = Product.retrieve_by_id(key_id)
    if not product:
        return redirect(url_for('pages.index'))
    return render_template(
        'product/get.html',
        product=product
    )

_blueprints = (mod,)
