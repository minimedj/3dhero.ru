# -*- coding: utf-8 -*-
from google.appengine.api import users
import flask
import flaskext.login
from mgi import util
from mgi.auth.decorators import login_required, admin_required
from mgi.auth.forms import ProfileUpdateForm
from mgi.auth.models import User
from mgi.auth.oauth_utils import (
    retrieve_user_from_google,
    retrieve_user_from_twitter, twitter,
    retrieve_user_from_facebook, facebook
)
from mgi.auth.utils import current_user_db, login_user_db

mod = flask.Blueprint(
    'mgi.auth',
    __name__,
    url_prefix='/mgi/auth',
    template_folder='templates'
)

mod_json = flask.Blueprint(
    'mgi.auth_json',
    __name__,
    url_prefix='/_json/mgi/auth',
    template_folder='templates'
)


@mod_json.route('/profile/', endpoint='profile')
@mod.route('/profile/', methods=['GET', 'POST'], endpoint='profile')
@login_required
def profile():
    form = ProfileUpdateForm()
    user_db = current_user_db()
    if form.validate_on_submit():
        user_db.name = form.name.data
        user_db.email = form.email.data.lower()
        user_db.put()
        return flask.redirect('/')
    if not form.errors:
        form.name.data = user_db.name
        form.email.data = user_db.email or ''

    if flask.request.path.startswith('/_json/'):
        return util.jsonify_model_db(user_db)

    return flask.render_template(
        'mgi/auth/profile.html',
        title='Profile',
        html_class='profile',
        form=form,
        user_db=user_db,
    )


@mod_json.route('/users/', endpoint='users')
@mod.route('/users/', endpoint='users')
@admin_required
def user_list():
    user_dbs, more_cursor = util.retrieve_dbs(
        User,
        User.query(),
        limit=util.param('limit', int),
        cursor=util.param('cursor'),
        order=util.param('order'),
        name=util.param('name'),
    )

    if flask.request.path.startswith('/_json/'):
        return util.jsonify_model_dbs(user_dbs, more_cursor)

    return flask.render_template(
        'mgi/auth/user_list.html',
        html_class='user',
        title='User List',
        user_dbs=user_dbs,
        more_url=util.generate_more_url(more_cursor),
    )


@mod.route('/login/')
def login():
    next_url = util.get_next_url()
    if flask.url_for('mgi.auth.login') in next_url:
        next_url = '/'

    google_login_url = flask.url_for('mgi.auth.login_google', next=next_url)
    twitter_login_url = flask.url_for('mgi.auth.login_twitter', next=next_url)
    facebook_login_url = flask.url_for('mgi.auth.login_facebook', next=next_url)

    return flask.render_template(
        'mgi/auth/login.html',
        title='Login',
        html_class='login',
        google_login_url=google_login_url,
        twitter_login_url=twitter_login_url,
        facebook_login_url=facebook_login_url,
        next_url=next_url
    )


@mod.route('/logout/')
def logout():
    flaskext.login.logout_user()
    return flask.redirect('/')


@mod.route('/login/google/')
def login_google():
    google_url = users.create_login_url(
        flask.url_for('mgi.auth_service.google_authorized',
            next=util.get_next_url())
    )
    return flask.redirect(google_url)


@mod.route('/login/twitter/')
def login_twitter():
    flask.session.pop('oauth_token', None)
    try:
        return twitter.authorize(
            callback=flask.url_for('mgi.auth_service.twitter_oauth_authorized',
                next=util.get_next_url()),
        )
    except:
        flask.flash(
            'Something went terribly wrong with Twitter login. Please try again.',
            category='danger',
        )
        return flask.redirect(
            flask.url_for('mgi.auth.login', next=util.get_next_url())
        )


@mod.route('/login/facebook/')
def login_facebook():
    return facebook.authorize(
        callback=flask.url_for('mgi.auth_service.facebook_authorized',
        next=util.get_next_url(),
        _external=True),
    )

mod_service = flask.Blueprint(
    'mgi.auth_service',
    __name__,
    url_prefix='/_s/mgi/auth',
    template_folder="templates"
)

@mod_service.route('/callback/google/authorized/')
def google_authorized():
    google_user = users.get_current_user()
    if google_user is None:
        flask.flash(u'You denied the request to sign in.')
        return flask.redirect(util.get_next_url())

    user_db = retrieve_user_from_google(google_user)
    return login_user_db(user_db)


@mod_service.route('/callback/twitter/oauth-authorized/')
@twitter.authorized_handler
def twitter_oauth_authorized(resp):
    if resp is None:
        flask.flash(u'You denied the request to sign in.')
        return flask.redirect(util.get_next_url())

    flask.session['oauth_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
        )
    user_db = retrieve_user_from_twitter(resp)
    return login_user_db(user_db)


@mod_service.route('/callback/facebook/oauth-authorized/')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            flask.request.args['error_reason'],
            flask.request.args['error_description']
            )
    flask.session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    user_db = retrieve_user_from_facebook(me.data)
    return login_user_db(user_db)

_blueprints = (mod, mod_json, mod_service,)