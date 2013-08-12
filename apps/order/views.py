# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, url_for, session, request, redirect
from flaskext.login import current_user
from apps.order.forms import OrderForm
from apps.order.models import Order, OrderProduct
from apps.product.models import Product
from auth import login_required
from apps.store_link.models import StoreLink

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
    store_links = StoreLink.query()
    if current_user.id <= 0:
        return render_template('order/login_require_box.html', store_links=store_links)
    if not current_user.is_order_box:
        return render_template('order/customer_require_box.html', store_links=store_links)
    product = Product.retrieve_by_id(key_id)
    if not product.is_available:
        return render_template('order/no_available_box.html', store_links=store_links)

    cart = session.get('cart', {})
    products = cart.get('products', {})

    order_product = products.get(key_id, {})
    order_product_count = order_product.get('count', 0)
    order_product_price = order_product.get('price', 0)

    if request.method == 'POST' and 'order_clear' in request.form:
        if key_id in products:
            del products[key_id]
            cart['products'] = products
            cart['price'] = cart.get('price', order_product_price) - order_product_price
            session['count'] = cart.get('count', order_product_count) - order_product_count
            session['cart'] = cart
        return redirect(url_for('order.get_order_box', key_id=key_id))

    order_product = products.get(key_id, {})
    order_product_count = order_product.get('count', 0)
    order_product_price = order_product.get('price', 0)

    if order_product_count:
        form = OrderForm(count=order_product_count)
        form.count.description=\
        u'В предзакаезе %s шт. данного товара на сумму %s рублей. Введите новое количество заказываемого товара.' \
        % (order_product_count, order_product_price)
        change = True
    else:
        form = OrderForm()
        change = False
    count=0
    if form.validate_on_submit():
        count = form.count.data
        if product:
            price = product.price_trade * count
            cart['price'] = cart.get('price', order_product_price) - order_product_price + price
            cart['products_count'] = cart.get('products_count', order_product_count) - order_product_count + count

            order_product['count'] = order_product_count = count
            order_product['price'] = order_product_price = order_product['count'] * product.price_trade

            products[key_id] = order_product
            cart['products']=products
            cart['un_products_count'] = len(products)
            session['cart'] = cart
            if count:
                change = True
                form.count.description=\
                u'В предзакаезе %s шт. данного товара на сумму %s рублей. Введите новое количество заказываемого товара.' \
                % (order_product_count, order_product_price)
    return render_template(
        'order/order_box.html',
        form=form,
        url=url_for('order.get_order_box', key_id=key_id),
        count=count,
        change=change,
        order_product_count=order_product_count,
        order_product_price=order_product_price,
        store_links=store_links
    )

def clear_cart():
    cart = {'price': 0, 'products_count': 0, 'un_products_count': 0}
    session['cart'] = cart

@mod.route('/cart/', methods=['GET', 'POST'])
@login_required
def cart_view():
    if request.method == 'POST' and 'order_delete' in request.form:
        clear_cart()
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
    if request.method == 'POST' and 'order_accept':
        order = Order(customer=current_user.user_db.key)
        price = 0
        for product in products:
            order_product = OrderProduct(
                name=product.name,
                img_url='%s=s100' % product.images[0] if product.images else '',
                product_key=product.key,
                count=product.order,
                price=product.order_price,
            )
            price += product.order_price
            order.products.append(order_product)
        order.price = price
        order.put()
        clear_cart()
        return render_template(
            'order/order_success.html',
            title=u'Предзаказ оформлен',
            order=order
        )
    return render_template(
        'order/cart.html',
        title=u'Оформление предзаказа',
        price=price,
        products_count=products_count,
        un_products_count=un_products_count,
        products=products
    )
