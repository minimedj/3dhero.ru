# -*- coding: utf-8 -*-
import sys
if not ('lib.zip' in sys.path):
    sys.path.insert(0, 'lib.zip')
import flask
import config

app = flask.Flask(__name__)
app.config.from_object(config)

import auth
import admin

from apps.pages.views import mod as pages_app
app.register_blueprint(pages_app)

from apps.api.v1.views import mod as api_v1_mod
from apps.api.v1.views import admin_mod as api_v1_mod_admin
app.register_blueprint(api_v1_mod)
app.register_blueprint(api_v1_mod_admin)

from apps.feedback.views import mod as feedback_mod
app.register_blueprint(feedback_mod)


