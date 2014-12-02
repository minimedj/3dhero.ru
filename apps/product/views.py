# -*- coding: utf-8 -*-
from flask import Blueprint, url_for, redirect, render_template
from apps.product.models import Product, CategoryProduct
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
    category = CategoryProduct.query(CategoryProduct.product_key == product.key).get()
    if category:
        category = category.section_key.get()
    return render_template(
        'product/get.html',
        html_class='product',
        title=product.strip_name,
        meta_keywords=product.meta_keywords or product.strip_name,
        product=product,
        category=category,
        back_url=back_url
    )

_blueprints = (mod,)
