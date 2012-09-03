# -*- coding: utf-8 -*-
try:
    # This part is surrounded in try/except because the this config.py file is
    # also used in the build.py script which is used to compile/minify the client
    # side files (*.less, *.coffee, *.js) and is not aware of the GAE
    from mgi.settings.models import Config

    config_db = Config.get_master_db()
    BRAND_NAME = config_db.brand_name
    ANALYTICS_ID = config_db.analytics_id
    SECRET_KEY = config_db.flask_secret_key
    PUBNUB_PUBLISH = config_db.pubnub_publish
    PUBNUB_SUBSCRIBE = config_db.pubnub_subscribe
except:
    pass

import os

CURRENT_VERSION_ID = os.environ.get('CURRENT_VERSION_ID', None)
if os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    DEVELOPMENT = False
else:
    DEVELOPMENT = True

PRODUCTION = not DEVELOPMENT
DEBUG = DEVELOPMENT

DEFAULT_DB_LIMIT = 64

INSTALLED_APPS = (
    'apps.pages',
    'apps.feedback',
    'apps.chat',
    'apps.extras',
    'apps.product',
    'apps.api.v1',
    'apps.file',
    'apps.product.admin',
)

################################################################################
# Client modules, also used by the build.py script.
################################################################################
STYLES = [
    'src/less/style.less',
    ]

SCRIPTS_MODULES = [
    'libs',
    'site',
    ]

SCRIPTS = {
    'libs': [
        'lib/jquery.js',
        'lib/pubnub.js',
        'lib/bootstrap/js/bootstrap-alert.js',
        'lib/bootstrap/js/bootstrap-button.js',
        'lib/bootstrap/js/bootstrap-dropdown.js',
        ],
    'site': [
        'src/coffee/common/util.coffee',
        'src/coffee/common/service.coffee',
        'src/coffee/common/common.coffee',
        'src/coffee/common/channel.coffee',

        'src/coffee/site/app.coffee',
        'src/coffee/site/profile.coffee',
        'src/coffee/site/admin.coffee',
        'src/coffee/site/chat.coffee',
        ],
    }
