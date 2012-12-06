# -*- coding: utf-8 -*-
from model import Base
from google.appengine.ext import ndb

class StoreLink(Base):
    name = ndb.StringProperty()
    link = ndb.StringProperty()
    description = ndb.TextProperty()