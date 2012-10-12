# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, url_for, session, request, redirect
from flaskext.login import current_user
from apps.order.forms import OrderForm
from apps.product.models import Product
from auth import login_required

mod = Blueprint(
    'order',
    __name__,
    url_prefix='/order',
    template_folder='templates'
)

@mod.route('/cart_box/')
def get_cart_box():
    price = 0
    if current_user.id > 0 and current_user.user_db.is_order_box:
        cart = session.get('cart', {})
        if not len(cart):
            cart['products_count'] = 0
            cart['price'] = 0
            cart['products'] = {}
            session['cart']=cart
        price = cart.get('price', 0)
    return render_template(
        'order/cart_box.html',
        price=price
    )

@mod.route('/order_box/<int:key_id>/', methods=['GET', 'POST'])
def get_order_box(key_id):
    if current_user.id <= 0:
        return render_template('order/login_require_box.html')
    if not current_user.is_order_box:
        return render_template('order/customer_require_box.html')
    product = Product.retrieve_by_id(key_id)
    if not product.is_available:
        return render_template('order/no_available_box.html')
    form = OrderForm()
    count=0
    if form.validate_on_submit():
        count = form.count.data
        if product:
            price = product.price_trade * count
            cart = session.get('cart', {})
            cart['price'] = cart.get('price', 0) + price
            cart['products_count'] = cart.get('products_count', 0) + count

            products = cart.get('products', {})
            pr = products.get(key_id, {})
            pr['count'] = pr.get('count', 0) + count
            pr['price'] = pr.get('price', 0) + (pr['count'] * product.price_trade)

            products[key_id] = pr
            cart['products']=products
            cart['un_products_count'] = len(products)
            session['cart'] = cart
    return render_template(
        'order/order_box.html',
        form=form,
        url=url_for('order.get_order_box', key_id=key_id),
        count=count
    )

@mod.route('/cart/', methods=['GET', 'POST'])
@login_required
def cart_view():
    if request.method == 'POST' and 'order_delete' in request.form:
        cart = {'price': 0}
        session['cart'] = cart
        return redirect(url_for('order.cart_view'))
    cart = session.get('cart', {})
    price = cart.get('price', 0)
    products_count = cart.get('products_count', 0)
    un_products_count = cart.get('un_products_count', 0)
    cart_products = cart.get('products', {})
    products = []
    for product_key in cart_products.keys():
        cart_product = cart_products.get(product_key, {})
        product = Product.retrieve_by_id(product_key)
        if product:
            product.order = cart_product.get('count', 0)
            product.order_price = cart_product.get('price', 0)
        products.append(product)
    return render_template(
        'order/cart.html',
        price=price,
        products_count=products_count,
        un_products_count=un_products_count,
        products=products
    )
