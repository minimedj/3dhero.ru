# -*- coding: utf-8 -*-
import re
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
    title_full = re.sub('[!"\'1-9]', '', product.name).split(' ')
    if len(title_full) >= 3:
        title = u' '.join(title_full[:3])
        title_full = ' '.join(title_full)
    else:
        title_full = ' '.join(title_full)
        title = title_full
    return render_template(
        'product/get.html',
        html_class='product',
        title=title,
        meta_keywords=title_full,
        meta_description=title_full,
        product=product,
        category=category,
        back_url=back_url
    )

_blueprints = (mod,)
