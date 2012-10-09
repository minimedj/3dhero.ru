# -*- coding: utf-8 -*-

from model import Base
from google.appengine.ext import ndb

class Contact(Base):
    order_id = ndb.IntegerProperty(default=0)
    is_public = ndb.BooleanProperty(default=False)
    title = ndb.StringProperty()
    zip_code = ndb.StringProperty()
    city = ndb.StringProperty()
    address = ndb.TextProperty()
    telephones = ndb.TextProperty()
    faxes = ndb.TextProperty()
    additional_info = ndb.TextProperty()
    geo = ndb.GeoPtProperty()