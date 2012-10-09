# -*- coding: utf-8 -*-

from flask import Blueprint, render_template
from flaskext.login import current_user

mod = Blueprint(
    'order',
    __name__,
    url_prefix='/order',
    template_folder='templates'
)

@mod.route('/cart_box/')
def get_cart_box():
    products = []
    products_count = 0
    return render_template(
        'order/cart_box.html',
        products = products,
        priducts_count = products_count
    )

@mod.route('/order_box/')
def get_order_box():
    if current_user.id <= 0:
        return render_template('order/login_require_box.html')
    if not current_user.user_db.is_order_box:
        return render_template('order/customer_require_box.html')
    return render_template('order/order_box.html')
