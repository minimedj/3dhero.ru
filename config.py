# -*- coding: utf-8 -*-
try:
    # This part is surrounded in try/except because the this config.py file is
    # also used in the build.py script which is used to compile/minify the client
    # side files (*.less, *.coffee, *.js) and is not aware of the GAE
    from model import Config

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

PRODUCTION = os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Eng')
DEVELOPMENT = not PRODUCTION
DEBUG = DEVELOPMENT

DEFAULT_DB_LIMIT = 64


################################################################################
# Client modules, also used by the build.py script.
################################################################################
STYLES = [
    'src/less/style.less',
]

SCRIPTS_MODULES = [
    'libs',
    'site',
    'jquery.plugins',
    'admin',
    'bootstrap-markdown',
]

SCRIPTS = {
    'libs': [
        'lib/jquery.js',
        'lib/bootstrap/js/bootstrap-alert.js',
        'lib/bootstrap/js/bootstrap-button.js',
        'lib/bootstrap/js/bootstrap-dropdown.js',
        'lib/bootstrap/js/bootstrap-tab.js',
        'lib/bootstrap/js/bootstrap-tooltip.js',
        'lib/bootstrap/js/bootstrap-popover.js',
        'lib/bootstrap/js/bootstrap-affix.js',
    ],
    'jquery.plugins': [
        'lib/jquery.mosaic.js',
        'lib/jquery.gmaps.js',
        'lib/jquery.form.js',
        'lib/jquery.tablesorter.js',
        'lib/jquery.metadata.js',
    ],
    'admin': [
        'lib/markdown/js/bootstrap-markdown.js',
        'lib/markdown/js/markdown.js',
        'lib/redactor.js'
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
        'src/coffee/site/cart_box.coffee',
#        'src/coffee/site/order_box.coffee',
    ],
}
