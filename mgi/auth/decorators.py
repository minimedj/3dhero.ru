import flask
import functools
from mgi.auth.utils import current_user_db, is_logged_in

def login_required(f):
  @functools.wraps(f)
  def decorated_function(*args, **kws):
    if is_logged_in():
      return f(*args, **kws)
    else:
      return flask.redirect(flask.url_for('login', next=flask.request.url))
  return decorated_function


def admin_required(f):
  @functools.wraps(f)
  def decorated_function(*args, **kws):
    if is_logged_in() and current_user_db().admin:
      return f(*args, **kws)
    else:
      flask.abort(401)
  return decorated_function