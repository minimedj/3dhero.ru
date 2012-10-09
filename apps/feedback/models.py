# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from model import Base

class Feedback(Base):
    subject = ndb.StringProperty()
    feedback = ndb.TextProperty()
    email = ndb.StringProperty(default='')
