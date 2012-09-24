# -*- coding: utf-8 -*-
import sys
if not ('lib.zip' in sys.path):
    sys.path.insert(0, 'lib.zip')
import flask
import config

app = flask.Flask(__name__)
app.config.from_object(config)

from apps.aside.views import get_aside, get_str_property
app.jinja_env.globals.update(get_aside=get_aside)
app.jinja_env.globals.update(get_str_property=get_str_property)

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

from apps.feedback.views import mod as feedback_mod
app.register_blueprint(feedback_mod)

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