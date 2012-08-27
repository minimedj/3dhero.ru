from google.appengine.ext import ndb
from mgi import util


class BaseX(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def retrieve_by_key_safe(cls, key_urlsafe):
        try:
            return ndb.Key(urlsafe=key_urlsafe).get()
        except:
            return None

    @classmethod
    def retrieve_by_id(cls, id):
        try:
            return cls.get_by_id(int(id))
        except ValueError:
            return None

    @classmethod
    def retrieve_one_by(cls, name, value):
        cls_db_list = cls.query(getattr(cls, name) == value).fetch(1)
        if cls_db_list:
            return cls_db_list[0]
        return None

    created_ago = ndb.ComputedProperty(
        lambda self: util.format_datetime_ago(self.created)\
        if self.modified else None
    )
    modified_ago = ndb.ComputedProperty(
        lambda self: util.format_datetime_ago(self.modified)\
        if self.modified else None
    )

    created_utc = ndb.ComputedProperty(
        lambda self: util.format_datetime_utc(self.created)\
        if self.modified else None
    )
    modified_utc = ndb.ComputedProperty(
        lambda self: util.format_datetime_utc(self.modified)\
        if self.modified else None
    )


class Base(BaseX):
    _PROPERTIES = {'key', 'id', 'created', 'modified', 'created_ago',
                   'modified_ago'
    }
