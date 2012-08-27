from google.appengine.api import users
import flask
import flaskext.oauth
from mgi.auth.models import User
from mgi.auth.utils import strip_username_from_email, generate_unique_username
from mgi.settings.models import Config

def retrieve_user_from_google(google_user):
  user_db = User.retrieve_one_by('federated_id', google_user.user_id())
  if user_db:
    return user_db
  user_db = User(
      federated_id=google_user.user_id(),
      name=strip_username_from_email(google_user.nickname()),
      username=generate_unique_username(google_user.nickname()),
      email=google_user.email().lower(),
      admin=users.is_current_user_admin(),
    )
  user_db.put()
  return user_db


twitter_oauth = flaskext.oauth.OAuth()
twitter = twitter_oauth.remote_app(
    'twitter',
    base_url='http://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=Config.get_master_db().twitter_consumer_key,
    consumer_secret=Config.get_master_db().twitter_consumer_secret,
)

@twitter.tokengetter
def get_twitter_token():
  return flask.session.get('oauth_token')


def retrieve_user_from_twitter(response):
  user_db = User.retrieve_one_by('twitter_id', response['user_id'])
  if user_db:
    return user_db
  user_db = User(
      twitter_id=response['user_id'],
      name=response['screen_name'],
      username=generate_unique_username(response['screen_name']),
    )
  user_db.put()
  return user_db


facebook_oauth = flaskext.oauth.OAuth()
facebook = facebook_oauth.remote_app(
    'facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=Config.get_master_db().facebook_app_id,
    consumer_secret=Config.get_master_db().facebook_app_secret,
    request_token_params={'scope': 'email'},
)

@facebook.tokengetter
def get_facebook_oauth_token():
    return flask.session.get('oauth_token')


def retrieve_user_from_facebook(response):
    user_db = User.retrieve_one_by('facebook_id', response['id'])
    if user_db:
        return user_db

    if 'username' in response:
        username = response['username']
    else:
        username = response['id']

    user_db = User(
        facebook_id=response['id'],
        name=response['name'],
        email=response['email'].lower(),
        username=generate_unique_username(username),
    )
    user_db.put()
    return user_db