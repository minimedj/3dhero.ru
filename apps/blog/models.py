# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from model import Base

class Post(Base):
    title = ndb.StringProperty(verbose_name=u'Заголовок', required=True)
    is_public = ndb.BooleanProperty(verbose_name=u'Публичная?')
    short_text = ndb.TextProperty(verbose_name=u'Краткое описание', required=True)
    text = ndb.TextProperty(verbose_name=u'Основной текст')
