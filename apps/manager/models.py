# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from model import Base

class Manager(Base):
    name = ndb.StringProperty(verbose_name=u'Имя')
    position = ndb.StringProperty()
    telephone = ndb.StringProperty()
    fax = ndb.StringProperty()
    mobile = ndb.StringProperty()
    email = ndb.StringProperty()
    icq = ndb.StringProperty()
    skype = ndb.StringProperty()
    is_public = ndb.BooleanProperty(default=False)

