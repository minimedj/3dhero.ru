# -*- coding: utf-8 -*-
from google.appengine.api import users
from auth import retrieve_user_from_google, login_user_db, twitter, retrieve_user_from_twitter, facebook, retrieve_user_from_facebook, login_required, ProfileUpdateForm, current_user_db
import flask
import flaskext.login
import util
from apps.order.models import PartnerRequest, REQUEST_STATUS

mod = flask.Blueprint(
    'auth',
    __name__
)

@mod.route('/login/')
def login():
  next_url = util.get_next_url()
  if flask.url_for('auth.login') in next_url:
    next_url = flask.url_for('pages.index')

  google_login_url = flask.url_for('auth.login_google', next=next_url)
  twitter_login_url = flask.url_for('auth.login_twitter', next=next_url)
  facebook_login_url = flask.url_for('auth.login_facebook', next=next_url)

  return flask.render_template(
      'auth/login.html',
      title='Login',
      html_class='login',
      google_login_url=google_login_url,
      twitter_login_url=twitter_login_url,
      facebook_login_url=facebook_login_url,
      next_url=next_url,
    )


@mod.route('/logout/')
def logout():
  flaskext.login.logout_user()
  return flask.redirect(flask.url_for('pages.index'))


@mod.route('/login/google/')
def login_google():
  google_url = users.create_login_url(
      flask.url_for('auth.google_authorized', next=util.get_next_url())
    )
  return flask.redirect(google_url)


@mod.route('/_s/callback/google/authorized/')
def google_authorized():
  google_user = users.get_current_user()
  if google_user is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  user_db = retrieve_user_from_google(google_user)
  return login_user_db(user_db)


@mod.route('/_s/callback/twitter/oauth-authorized/')
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


@mod.route('/login/twitter/')
def login_twitter():
  flask.session.pop('oauth_token', None)
  try:
    return twitter.authorize(
        callback=flask.url_for('auth.twitter_oauth_authorized',
        next=util.get_next_url()),
      )
  except:
    flask.flash(
        'Something went terribly wrong with Twitter login. Please try again.',
        category='danger',
      )
    return flask.redirect(flask.url_for('auth.login', next=util.get_next_url()))


@mod.route('/_s/callback/facebook/oauth-authorized/')
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


@mod.route('/login/facebook/')
def login_facebook():
  return facebook.authorize(callback=flask.url_for('auth.facebook_authorized',
      next=util.get_next_url(),
      _external=True),
    )


@mod.route('/_json/profile/', endpoint='profile_service')
@mod.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
  next_url = util.get_next_url()
  customer_fields_require = False
  user_db = current_user_db()
  form = ProfileUpdateForm(obj=user_db)
  if form.validate_on_submit():
    form.populate_obj(user_db)
    user_db.put()
    if not 'customer_require' in flask.request.form:
      flask.flash(u'Профиль успешно обновлен')
      return flask.redirect(flask.url_for('pages.index'))
    else:
      if not form.telephone.data \
         or not form.company.data\
         or not form.address.data\
         or not form.city.data:
        customer_fields_require = True
      else:
        msg = u'Профиль успешно обновлен, '
        request = PartnerRequest.query(PartnerRequest.customer == user_db.key)
        if request.count():
            msg += u'Вы уже делали запрос на сотрудничество, запрос '
            request = request.get()
            if request.status == REQUEST_STATUS['now']:
                msg += u'еще не рассмотрен'
            elif request.status == REQUEST_STATUS['accept']:
                msg += u'одобрен'
            elif request.status == REQUEST_STATUS['admin']:
                msg += u'одобрен и Вам были даны права администратора'
            else:
                msg += u'отклонен'
        else:
            msg += u'в ближайшее время с Вами свяжется наш менеджер'
            request = PartnerRequest(customer = user_db.key)
            request.put()
        flask.flash(msg)
        return flask.redirect(flask.url_for('pages.index'))

  if flask.request.path.startswith('/_json/'):
    return util.jsonify_model_db(user_db)

  return flask.render_template(
      'auth/profile.html',
      title='Profile',
      html_class='profile',
      form=form,
      user_db=user_db,
      customer_fields_require = customer_fields_require,
      next_url = next_url
    )