from google.appengine.ext import ndb
import os
from mgi.models import Base


class ConfigX(object):
    @classmethod
    def get_master_db(cls):
        return cls.get_or_insert('master')


class Config(Base, ConfigX):
    analytics_id = ndb.StringProperty(default='')
    brand_name = ndb.StringProperty(default='GAE Init')
    facebook_app_id = ndb.StringProperty(default='')
    facebook_app_secret = ndb.StringProperty(default='')
    feedback_email = ndb.StringProperty(default='')
    flask_secret_key = ndb.StringProperty(default='%r' % os.urandom(24))
    pubnub_publish = ndb.StringProperty(default='')
    pubnub_secret = ndb.StringProperty(default='')
    pubnub_subscribe = ndb.StringProperty(default='')
    twitter_consumer_key = ndb.StringProperty(default='')
    twitter_consumer_secret = ndb.StringProperty(default='')
    _PROPERTIES = Base._PROPERTIES.union(set([
        'analytics_id', 'brand_name', 'facebook_app_id',
        'facebook_app_secret', 'feedback_email', 'flask_secret_key',
        'pubnub_publish', 'pubnub_subscribe', 'twitter_consumer_key',
        'twitter_consumer_secret'
    ]))
