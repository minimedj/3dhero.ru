# -*- coding: utf-8 -*-
import sys
if not ('lib.zip' in sys.path):
    sys.path.insert(0, 'lib.zip')
import flask
import config

app = flask.Flask(__name__)
app.config.from_object(config)

from apps.aside.views import get_aside, get_str_property, date_str
app.jinja_env.globals.update(get_aside=get_aside)
app.jinja_env.globals.update(get_str_property=get_str_property)
app.jinja_env.globals.update(date_str=date_str)

from auth_views import mod as auth_mod
app.register_blueprint(auth_mod)

from admin_views import mod as admin_mod
from admin_views import json_mod as json_admin_mod
app.register_blueprint(admin_mod)
app.register_blueprint(json_admin_mod)

from apps.pages.views import mod as pages_app
app.register_blueprint(pages_app)

from apps.api.v1.views import mod as api_v1_mod
from apps.api.v1.views import admin_mod as api_v1_mod_admin
app.register_blueprint(api_v1_mod)
app.register_blueprint(api_v1_mod_admin)

from apps.api.v2.views import mod as api_v2_mod
app.register_blueprint(api_v2_mod)

from apps.feedback.views import mod as feedback_mod
from apps.feedback.admin.views import mod as admin_feedback_mod
app.register_blueprint(feedback_mod)
app.register_blueprint(admin_feedback_mod)

from apps.product.admin.views import mod as admin_product
app.register_blueprint(admin_product)

from apps.product.admin.tasks import mod as product_task_mod
app.register_blueprint(product_task_mod)

from apps.product.views import mod as product_mod
app.register_blueprint(product_mod)

from apps.file.views import mod as file_view
app.register_blueprint(file_view)

from apps.file.admin.views import mod as file_admin_mod
app.register_blueprint(file_admin_mod)

from apps.blog.admin.views import mod as blog_admin_mod
app.register_blueprint(blog_admin_mod)

from apps.blog.views import mod as blog_mod
app.register_blueprint(blog_mod)

from apps.order.views import mod as order_mod
app.register_blueprint(order_mod)

from apps.order.admin.views import mod as admin_order_mod
app.register_blueprint(admin_order_mod)

from apps.manager.admin.views import mod as manager_admin_mod
app.register_blueprint(manager_admin_mod)

from apps.contact.admin.views import mod as admin_contact_mod
app.register_blueprint(admin_contact_mod)

from apps.user.admin.views import mod as admin_user_mod
from apps.user.admin.views import mod_json as json_admin_user_mod
app.register_blueprint(admin_user_mod)
app.register_blueprint(json_admin_user_mod)

from apps.price.admin.views import mod as admin_price_mod
app.register_blueprint(admin_price_mod)

from apps.price.views import mod as price_mod
app.register_blueprint(price_mod)

from apps.store_link.admin.views import mod as admin_store_link
app.register_blueprint(admin_store_link)

from apps.search.views import mod as search_mod
app.register_blueprint(search_mod)

@app.errorhandler(401)
def custom_401(error):
    return flask.redirect(flask.url_for('auth.login', next=flask.request.url))
