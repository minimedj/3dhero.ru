# -*- coding: utf-8 -*-
import sys
import flask
import config
from mgi import install_apps, install_login_manager

if not ('lib.zip' in sys.path):
    sys.path.insert(0, 'lib.zip')

app = flask.Flask(__name__)
app.config.from_object(config)
install_apps(app, config)
install_login_manager(app)
