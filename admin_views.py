# -*- coding: utf-8 -*-
from admin import ConfigUpdateForm, update_config_variables
from auth import admin_required
import flask
import model
import util

mod = flask.Blueprint(
    'admin',
    __name__,
    url_prefix='/admin'
)

json_mod = flask.Blueprint(
    'json.admin',
    __name__,
    url_prefix='/_json'
)

@json_mod.route('/admin/')
@mod.route('/', methods=['GET', 'POST'])
@admin_required
def config_update():
    form = ConfigUpdateForm()

    config_db = model.Config.get_master_db()
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
        return flask.redirect(flask.url_for('admin.config_update'))
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
        'admin/config_update.html',
        title=u'Общие настройки',
        html_class='admin-config',
        form=form,
        config_db=config_db,
    )