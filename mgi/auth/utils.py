# -*- coding: utf-8 -*-
import flask
import flaskext.login
from mgi.auth import login_manager
from mgi.util import get_next_url
from mgi.auth.models import FlaskUser, User
from mgi.settings.models import Config

def current_user_id():
    return flaskext.login.current_user.id

def current_user_key():
  return flaskext.login.current_user.user_db.key

def current_user_db():
    return current_user_key().get()

def is_logged_in():
    return current_user_id() != 0

def login_user_db(user_db):
  if not user_db:
    return flask.redirect(flask.url_for('mgi.auth.login'))

  flask_user_db = FlaskUser(user_db)
  if flaskext.login.login_user(flask_user_db):
    flask.flash('Welcome on %s %s!!!' % (
        Config.get_master_db().brand_name, user_db.name
      ), category='success')
    return flask.redirect(get_next_url())
  else:
    flask.flash('Sorry, but you could not log in.', category='danger')
    return flask.redirect(flask.url_for('mgi.auth.login'))


def strip_username_from_email(email):
  #TODO: use re
  if email.find('@') > 0:
    email = email[0:email.find('@')]
  return email.lower()


def generate_unique_username(username):
  username = strip_username_from_email(username)

  new_username = username
  n = 1
  while User.retrieve_one_by('username', new_username) is not None:
    new_username = '%s%d' % (username, n)
    n += 1
  return new_username


@login_manager.user_loader
def load_user(key):
  user_db = User.retrieve_by_key_safe(key)
  if user_db:
    return FlaskUser(user_db)
  return None