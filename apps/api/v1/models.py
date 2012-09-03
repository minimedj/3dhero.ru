# -*- coding: utf-8 -*-
from mgi.models import Base
from mgi.util import uuid
from google.appengine.ext import ndb


class WriteKey(Base):
    email = ndb.StringProperty()
    api_key = ndb.StringProperty()

    def _pre_put_hook(self):
        if not self.api_key:
            self.api_key = uuid()

