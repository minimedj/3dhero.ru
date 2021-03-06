# -*- coding: utf-8 -*-
import os
from google.appengine.ext import ndb
import modelx


class Base(ndb.Model, modelx.BaseX):
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  _PROPERTIES = {
      'key', 'id', 'created', 'modified', 'created_ago', 'modified_ago'
    }


class Config(Base, modelx.ConfigX):
  analytics_id = ndb.StringProperty(default='')
  brand_name = ndb.StringProperty(default='GAE Init')
  facebook_app_id = ndb.StringProperty(default='')
  facebook_app_secret = ndb.StringProperty(default='')
  vk_app_id = ndb.StringProperty(default='')
  vk_app_secret = ndb.StringProperty(default='')
  ya_app_id = ndb.StringProperty(default='')
  ya_app_secret = ndb.StringProperty(default='')
  mailru_app_id = ndb.StringProperty(default='')
  mailru_app_secret = ndb.StringProperty(default='')
  odnoklassniki_app_id = ndb.StringProperty(default='')
  odnoklassniki_app_public = ndb.StringProperty(default='')
  odnoklassniki_app_secret = ndb.StringProperty(default='')
  feedback_email = ndb.StringProperty(default='')
  flask_secret_key = ndb.StringProperty(default='%r' % os.urandom(24))
  pubnub_publish = ndb.StringProperty(default='')
  pubnub_secret = ndb.StringProperty(default='')
  pubnub_subscribe = ndb.StringProperty(default='')
  twitter_consumer_key = ndb.StringProperty(default='')
  twitter_consumer_secret = ndb.StringProperty(default='')
  recaptcha_public_key = ndb.StringProperty(default='')
  recaptcha_private_key = ndb.StringProperty(default='')
  _PROPERTIES = Base._PROPERTIES.union({
      'analytics_id',
      'brand_name',
      'facebook_app_id',
      'facebook_app_secret',
      'feedback_email',
      'flask_secret_key',
      'pubnub_publish',
      'pubnub_subscribe',
      'twitter_consumer_key',
      'twitter_consumer_secret',
    })


class User(Base, modelx.UserX):
  name = ndb.StringProperty(indexed=True, required=True)
  username = ndb.StringProperty(indexed=True, required=True)

  email = ndb.StringProperty(default='')
  telephone = ndb.StringProperty(verbose_name=u'Телефон', default='')
  company = ndb.StringProperty(verbose_name=u'Компания', default='')
  city = ndb.StringProperty(verbose_name=u'Город', default='')
  address = ndb.TextProperty(verbose_name=u'Адрес', default='')

  active = ndb.BooleanProperty(default=True)
  admin = ndb.BooleanProperty(default=False)
  is_customer = ndb.BooleanProperty(default=False)
  is_order_box = ndb.ComputedProperty(lambda self: True if self.admin or self.is_customer else False)

  _PROPERTIES = Base._PROPERTIES.union({
      'name', 'username', 'avatar_url', 'email', 'telephone', 'company', 'city', 'address'
    })

  def _pre_put_hook(self):
      if self.email:
          self.email = self.email.lower()
