# -*- coding: utf-8 -*-
from google.appengine.api import users
from auth import retrieve_user_from_google, login_user_db, twitter, retrieve_user_from_twitter, facebook, retrieve_user_from_facebook, vk, retrieve_user_from_vk, yandex, retrieve_user_from_yandex, mailru, retrieve_user_from_mailru, login_required, ProfileUpdateForm, current_user_db
import flask
from werkzeug.urls import url_encode
import flaskext.login
from flaskext.oauth import add_query, parse_response, OAuthException
import util
from apps.order.models import PartnerRequest, REQUEST_STATUS
import hashlib
from urllib2 import Request, urlopen
from urllib import urlencode
import json


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
  vk_login_url = flask.url_for('auth.login_vk', next=next_url)
  yandex_login_url = flask.url_for('auth.login_yandex', next=next_url)
  mailru_login_url = flask.url_for('auth.login_mailru', next=next_url)

  return flask.render_template(
      'auth/login.html',
      title='Login',
      html_class='login',
      google_login_url=google_login_url,
      twitter_login_url=twitter_login_url,
      facebook_login_url=facebook_login_url,
      vk_login_url=vk_login_url,
      yandex_login_url=yandex_login_url,
      mailru_login_url=mailru_login_url,
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


@mod.route('/_s/callback/yandex/oauth-authorized/')
def yandex_authorized():
  user_db = None
  state = flask.request.args.get('state')
  try:
      remote_args = {
            'code':             flask.request.args.get('code'),
            'client_id':        yandex.consumer_key,
            'client_secret':    yandex.consumer_secret,
            'grant_type': 'authorization_code'
        }
      remote_args.update(yandex.access_token_params)
      if yandex.access_token_method == 'POST':
        resp, content = yandex._client.request(yandex.expand_url(yandex.access_token_url),
                                                 yandex.access_token_method,
                                                 url_encode(remote_args))
      elif yandex.access_token_method == 'GET':
        url = add_query(yandex.expand_url(yandex.access_token_url), remote_args)
        resp, content = yandex._client.request(url, yandex.access_token_method)
      else:
        raise OAuthException('Unsupported access_token_method: ' +
                                 yandex.access_token_method)
      data = parse_response(resp, content)
      if not yandex.status_okay(resp):
        raise OAuthException('Invalid response from ' + yandex.name,
                                 type='invalid_response', data=data)

      if resp is None:
        return 'Access denied: reason=%s error=%s' % (
          flask.request.args['error_reason'],
          flask.request.args['error_description']
        )
      flask.session['oauth_token'] = (data['access_token'], '')
      me = yandex.get('/info')
      user_db = retrieve_user_from_yandex(me.data)
  except:
    pass
  redirect_url = login_user_db(user_db)
  if state:
      return flask.redirect(state)
  return redirect_url

@mod.route('/login/yandex/')
def login_yandex():
  params = dict(yandex.request_token_params)
  params['client_id'] = yandex.consumer_key
  params['response_type'] = 'code'
  params['state'] = util.get_next_url()
  flask.session[yandex.name + '_oauthredir'] = flask.url_for('auth.yandex_authorized')
  url = add_query(yandex.expand_url(yandex.authorize_url), params)
  return flask.redirect(url)

def mailru_sig(data):
  param_list = sorted(list(item + '=' + data[item] for item in data))
  return hashlib.md5(''.join(param_list) + mailru.consumer_secret).hexdigest()

@mod.route('/_s/callback/mailru/oauth-authorized/')
@mailru.authorized_handler
def mailru_authorized(resp):
  if resp is None:
    return 'Access denied: reason=%s error=%s' % (
      flask.request.args['error_reason'],
      flask.request.args['error_description']
    )
  access_token = resp['access_token']
  flask.session['oauth_token'] = (access_token, '')
  try:
    data={
    'method':'users.getInfo',
    'app_id':mailru.consumer_key,
    'session_key':access_token,
    'secure':'1'
    }
    data['sig']=mailru_sig(data)
    params = urlencode(data)
    url = mailru.base_url + 'platform/api'
    request = Request(url, params)
    mailru_resp = json.loads(urlopen(request).read())
    user_db = retrieve_user_from_mailru(mailru_resp[0])
  except:
    flask.flash(
      u'Упс, что-то пошло не так, попробуйте зайти позже.',
      category='danger'
    )
    return flask.redirect(flask.url_for('auth.login', next=util.get_next_url()))
  return login_user_db(user_db)


@mod.route('/login/mailru/')
def login_mailru():
    flask.session.pop('oauth_token', None)
    return mailru.authorize(callback=flask.url_for('auth.mailru_authorized',
    next=util.get_next_url(),
    _external=True)
    )

@mod.route('/_s/callback/vk/oauth-authorized/')
@vk.authorized_handler
def vk_authorized(resp):
  if resp is None:
    return 'Access denied: reason=%s error=%s' % (
      flask.request.args['error_reason'],
      flask.request.args['error_description']
    )
  access_token = resp['access_token']
  flask.session['oauth_token'] = (access_token, '')
  me = vk.get('/method/getUserInfoEx', data={'access_token':access_token})
  user_db = retrieve_user_from_vk(me.data['response'])
  return login_user_db(user_db)


@mod.route('/login/vk/')
def login_vk():
  return vk.authorize(callback=flask.url_for('auth.vk_authorized',
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