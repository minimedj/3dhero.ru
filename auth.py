# -*- coding: utf-8 -*-
from google.appengine.api import users
import functools

import flask
import flaskext.login
import flaskext.oauth
from flaskext import wtf
from main import app

import util
import model


################################################################################
# Flaskext Login
################################################################################
login_manager = flaskext.login.LoginManager()


class AnonymousUser(flaskext.login.AnonymousUser):
  id = 0
  admin = False
  name = 'Anonymous'

  def key(self):
    return None

login_manager.anonymous_user = AnonymousUser


class FlaskUser(AnonymousUser):
  def __init__(self, user_db):
    self.user_db = user_db
    self.id = user_db.key.id()
    self.name = user_db.name
    self.admin = user_db.admin

  def key(self):
    return self.user_db.key.urlsafe()

  def get_id(self):
    return self.user_db.key.urlsafe()

  def is_authenticated(self):
    return True

  def is_active(self):
    return self.user_db.active

  def is_anonymous(self):
    return False


@login_manager.user_loader
def load_user(key):
  user_db = model.User.retrieve_by_key_safe(key)
  if user_db:
    return FlaskUser(user_db)
  return None


login_manager.setup_app(app)


def current_user_id():
  return flaskext.login.current_user.id


def current_user_key():
  return flaskext.login.current_user.user_db.key


def current_user_db():
  return current_user_key().get()


def is_logged_in():
  return current_user_id() != 0


def login_required(f):
  @functools.wraps(f)
  def decorated_function(*args, **kws):
    if is_logged_in():
      return f(*args, **kws)
    else:
      return flask.redirect(flask.url_for('auth.login', next=flask.request.url))
  return decorated_function


def admin_required(f):
  @functools.wraps(f)
  def decorated_function(*args, **kws):
    if is_logged_in() and current_user_db().admin:
      return f(*args, **kws)
    else:
      flask.abort(401)
  return decorated_function


################################################################################
# Login stuff
################################################################################
@app.route('/login/', endpoint='auth.login')
def login():
  next_url = util.get_next_url()
  if flask.url_for('auth.login') in next_url:
    next_url = flask.url_for('pages.index')

  google_login_url = flask.url_for('login_google', next=next_url)
  twitter_login_url = flask.url_for('login_twitter', next=next_url)
  facebook_login_url = flask.url_for('login_facebook', next=next_url)

  return flask.render_template(
      'auth/login.html',
      title='Login',
      html_class='login',
      google_login_url=google_login_url,
      twitter_login_url=twitter_login_url,
      facebook_login_url=facebook_login_url,
      next_url=next_url,
    )


@app.route('/logout/', endpoint='auth.logout')
def logout():
  flaskext.login.logout_user()
  return flask.redirect(flask.url_for('pages.index'))


################################################################################
# Google
################################################################################
@app.route('/login/google/')
def login_google():
  google_url = users.create_login_url(
      flask.url_for('google_authorized', next=util.get_next_url())
    )
  return flask.redirect(google_url)


@app.route('/_s/callback/google/authorized/')
def google_authorized():
  google_user = users.get_current_user()
  if google_user is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  user_db = retrieve_user_from_google(google_user)
  return login_user_db(user_db)


def retrieve_user_from_google(google_user):
  user_db = model.User.retrieve_one_by('federated_id', google_user.user_id())
  if user_db:
    return user_db
  user_db = model.User(
      federated_id=google_user.user_id(),
      name=strip_username_from_email(google_user.nickname()),
      username=generate_unique_username(google_user.nickname()),
      email=google_user.email().lower(),
      admin=users.is_current_user_admin(),
    )
  user_db.put()
  return user_db


################################################################################
# Twitter
################################################################################
twitter_oauth = flaskext.oauth.OAuth()


twitter = twitter_oauth.remote_app(
    'twitter',
    base_url='http://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=model.Config.get_master_db().twitter_consumer_key,
    consumer_secret=model.Config.get_master_db().twitter_consumer_secret,
  )


@app.route('/_s/callback/twitter/oauth-authorized/')
@twitter.authorized_handler
def twitter_oauth_authorized(resp):
  if resp is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (
    resp['oauth_token'],
    resp['oauth_token_secret']
  )
  user_db = retrieve_user_from_twitter(resp)
  return login_user_db(user_db)


@twitter.tokengetter
def get_twitter_token():
  return flask.session.get('oauth_token')


@app.route('/login/twitter/')
def login_twitter():
  flask.session.pop('oauth_token', None)
  try:
    return twitter.authorize(
        callback=flask.url_for('twitter_oauth_authorized',
        next=util.get_next_url()),
      )
  except:
    flask.flash(
        'Something went terribly wrong with Twitter login. Please try again.',
        category='danger',
      )
    return flask.redirect(flask.url_for('auth.login', next=util.get_next_url()))


def retrieve_user_from_twitter(response):
  user_db = model.User.retrieve_one_by('twitter_id', response['user_id'])
  if user_db:
    return user_db
  user_db = model.User(
      twitter_id=response['user_id'],
      name=response['screen_name'],
      username=generate_unique_username(response['screen_name']),
    )
  user_db.put()
  return user_db


################################################################################
# Facebook
################################################################################
facebook_oauth = flaskext.oauth.OAuth()

facebook = facebook_oauth.remote_app(
    'facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=model.Config.get_master_db().facebook_app_id,
    consumer_secret=model.Config.get_master_db().facebook_app_secret,
    request_token_params={'scope': 'email'},
  )


@app.route('/_s/callback/facebook/oauth-authorized/')
@facebook.authorized_handler
def facebook_authorized(resp):
  if resp is None:
    return 'Access denied: reason=%s error=%s' % (
      flask.request.args['error_reason'],
      flask.request.args['error_description']
    )
  flask.session['oauth_token'] = (resp['access_token'], '')
  me = facebook.get('/me')
  user_db = retrieve_user_from_facebook(me.data)
  return login_user_db(user_db)


@facebook.tokengetter
def get_facebook_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/login/facebook/')
def login_facebook():
  return facebook.authorize(callback=flask.url_for('facebook_authorized',
      next=util.get_next_url(),
      _external=True),
    )


def retrieve_user_from_facebook(response):
  user_db = model.User.retrieve_one_by('facebook_id', response['id'])
  if user_db:
    return user_db

  if 'username' in response:
    username = response['username']
  else:
    username = response['id']

  user_db = model.User(
      facebook_id=response['id'],
      name=response['name'],
      email=response['email'].lower(),
      username=generate_unique_username(username),
    )
  user_db.put()
  return user_db


################################################################################
# Helpers
################################################################################
def login_user_db(user_db):
  if not user_db:
    return flask.redirect(flask.url_for('auth.login'))

  flask_user_db = FlaskUser(user_db)
  if flaskext.login.login_user(flask_user_db):
    flask.flash('Welcome on %s %s!!!' % (
        model.Config.get_master_db().brand_name, user_db.name
      ), category='success')
    return flask.redirect(util.get_next_url())
  else:
    flask.flash('Sorry, but you could not log in.', category='danger')
    return flask.redirect(flask.url_for('auth.login'))


def strip_username_from_email(email):
  #TODO: use re
  if email.find('@') > 0:
    email = email[0:email.find('@')]
  return email.lower()


def generate_unique_username(username):
  username = strip_username_from_email(username)

  new_username = username
  n = 1
  while model.User.retrieve_one_by('username', new_username) is not None:
    new_username = '%s%d' % (username, n)
    n += 1
  return new_username

class ProfileUpdateForm(wtf.Form):
  name = wtf.TextField('Name', [wtf.validators.required()])
  email = wtf.TextField('Email', [
      wtf.validators.optional(),
      wtf.validators.email("That doesn't look like an email"),
    ])


@app.route('/_s/profile/', endpoint='profile_service')
@app.route('/profile/', methods=['GET', 'POST'], endpoint='auth.profile')
@login_required
def profile():
  form = ProfileUpdateForm()
  user_db = current_user_db()
  if form.validate_on_submit():
    user_db.name = form.name.data
    user_db.email = form.email.data.lower()
    user_db.put()
    return flask.redirect(flask.url_for('pages.index'))
  if not form.errors:
    form.name.data = user_db.name
    form.email.data = user_db.email or ''

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_db(user_db)

  return flask.render_template(
      'auth/profile.html',
      title='Profile',
      html_class='profile',
      form=form,
      user_db=user_db,
    )