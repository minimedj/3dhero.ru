# -*- coding: utf-8 -*-
from werkzeug.utils import import_string
from mgi.auth import login_manager


_INTERNAL_INSTALLED_APPS = (
    'mgi.auth',
    'mgi.settings',
)

def install_apps(app, config):
    for url_module in _INTERNAL_INSTALLED_APPS + config.INSTALLED_APPS:
        mod = import_string(''.join((url_module,'.views')))
        bps = getattr(mod, "_blueprints")
        for bp in bps:
            app.register_blueprint(bp)

def install_login_manager(app):
    login_manager.setup_app(app)
