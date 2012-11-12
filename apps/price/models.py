# -*- coding: utf-8 -*-

from apps.file.models import File
from google.appengine.ext import ndb
from model import Base
from werkzeug.wrappers import cached_property

class PriceFile(Base):
    order_id = ndb.IntegerProperty(
        default=0,
        verbose_name=u'Порядок сортиовки'
    )
    file = ndb.KeyProperty(File)

    @cached_property
    def get_file(self):
        if self.file:
            return self.file.get()
        else:
            return None

    @classmethod
    def _pre_delete_hook(cls, key):
        obj = key.get()
        if obj and obj.file:
            obj.file.delete()