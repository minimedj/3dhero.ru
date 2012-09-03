import hashlib
from google.appengine.ext import ndb
import flaskext.login
from mgi.models import Base


class UserX(object):
    avatar_url = ndb.ComputedProperty(
        lambda self: 'http://www.gravatar.com/avatar/%s?d=identicon&r=x' % (
            hashlib.md5(self.email or self.name).hexdigest().lower()
            )
    )


class User(Base, UserX):
    name = ndb.StringProperty(indexed=True, required=True)
    username = ndb.StringProperty(indexed=True, required=True)
    email = ndb.StringProperty(default='')

    active = ndb.BooleanProperty(default=True)
    admin = ndb.BooleanProperty(default=False)

    federated_id = ndb.StringProperty(default='')
    facebook_id = ndb.StringProperty(default='')
    twitter_id = ndb.StringProperty(default='')

    _PROPERTIES = Base._PROPERTIES.union(
        set(['name', 'username', 'avatar_url']))


class AnonymousUser(flaskext.login.AnonymousUser):
    id = 0
    admin = False
    name = 'Anonymous'

    def key(self):
        return None


class FlaskUser(AnonymousUser):
    def __init__(self, user_db):
        self.user_db = user_db
        self.id = user_db.key.id()
        self.name = user_db.name
        self.admin = user_db.admin

    def key(self):
        return self.user_db.key.urlsafe()

    def get_id(self):
        return self.user_db.key.urlsafe()

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.user_db.active

    def is_anonymous(self):
        return False
