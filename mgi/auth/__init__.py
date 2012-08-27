# -*- coding: utf-8 -*-
import flaskext.login
from mgi.auth.models import AnonymousUser


################################################################################
# Flaskext Login
################################################################################

login_manager = flaskext.login.LoginManager()
login_manager.anonymous_user = AnonymousUser
