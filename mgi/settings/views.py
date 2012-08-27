# -*- coding: utf-8 -*-
import flask
from mgi import util
from mgi.settings.forms import ConfigUpdateForm
from mgi.settings.models import Config
from mgi.auth.decorators import admin_required

mod = flask.Blueprint(
    'mgi.settings',
    __name__,
    url_prefix='/mgi/settings',
    template_folder='templates'
)


mod_json = flask.Blueprint(
    'mgi.settings_json',
    __name__,
    url_prefix='/_json/mgi/settings',
    template_folder='templates'
)

@mod_json.route('/config/', endpoint='config')
@mod.route('/config/', methods=['GET', 'POST'], endpoint='config')
@admin_required
def index():
  form = ConfigUpdateForm()

  config_db = Config.get_master_db()
  if form.validate_on_submit():
    config_db.analytics_id = form.analytics_id.data
    config_db.brand_name = form.brand_name.data
    config_db.facebook_app_id = form.facebook_app_id.data
    config_db.facebook_app_secret = form.facebook_app_secret.data
    config_db.feedback_email = form.feedback_email.data
    config_db.flask_secret_key = form.flask_secret_key.data
    config_db.pubnub_publish = form.pubnub_publish.data
    config_db.pubnub_secret = form.pubnub_secret.data
    config_db.pubnub_subscribe = form.pubnub_subscribe.data
    config_db.twitter_consumer_key = form.twitter_consumer_key.data
    config_db.twitter_consumer_secret = form.twitter_consumer_secret.data
    config_db.put()
    update_config_variables(config_db)
    flask.flash('Your Config settings have been saved', category='success')
    return flask.redirect('/')
  if not form.errors:
    form.analytics_id.data = config_db.analytics_id
    form.brand_name.data = config_db.brand_name
    form.facebook_app_id.data = config_db.facebook_app_id
    form.facebook_app_secret.data = config_db.facebook_app_secret
    form.feedback_email.data = config_db.feedback_email
    form.flask_secret_key.data = config_db.flask_secret_key
    form.pubnub_publish.data = config_db.pubnub_publish
    form.pubnub_secret.data = config_db.pubnub_secret
    form.pubnub_subscribe.data = config_db.pubnub_subscribe
    form.twitter_consumer_key.data = config_db.twitter_consumer_key
    form.twitter_consumer_secret.data = config_db.twitter_consumer_secret

  if flask.request.path.startswith('/_json/'):
    return util.jsonify_model_db(config_db)

  return flask.render_template(
      'mgi/settings/config_update.html',
      title='Admin Config',
      html_class='admin-config',
      form=form,
      config_db=config_db,
    )


def update_config_variables(config_db):
  from main import app
  app.config.update(
      BRAND_NAME=config_db.brand_name,
      ANALYTICS_ID=config_db.analytics_id,
      SECRETE_KEY=config_db.flask_secret_key,
    )

_blueprints = (mod, mod_json, )