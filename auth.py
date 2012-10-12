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
    is_order_box = False
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
        self.is_order_box = user_db.is_order_box

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
            return flask.redirect(
                flask.url_for('auth.login', next=flask.request.url))

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
# Google
################################################################################
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


@twitter.tokengetter
def get_twitter_token():
    return flask.session.get('oauth_token')


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


@facebook.tokengetter
def get_facebook_oauth_token():
    return flask.session.get('oauth_token')


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
    name = wtf.TextField(
        u'Имя',
        [wtf.validators.required()]
    )
    email = wtf.TextField(
        u'Email',
        [
            wtf.validators.optional(),
            wtf.validators.email(u'Это не похоже на Email')
        ],
        description=u'Введите Ваш Email'
    )
    company = wtf.TextField(
        u'Компания',
        description=u'Укажите название Вашей организации'
    )
    telephone = wtf.TextField(
        u'Телефон',
        description=u'В случае городского телефона не забудьте указать код города')
    city = wtf.TextField(u'Город')
    address = wtf.TextAreaField(
        u'Адрес',
        description=u'Введите полный адрес Вашей организации'
    )
