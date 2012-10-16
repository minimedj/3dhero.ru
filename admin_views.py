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
    config_db = model.Config.get_master_db()
    form = ConfigUpdateForm(obj=config_db)
    if form.validate_on_submit():
        form.populate_obj(config_db)
        config_db.put()
        update_config_variables(config_db)
        flask.flash('Your Config settings have been saved', category='success')
        return flask.redirect(flask.url_for('admin.config_update'))
    if flask.request.path.startswith('/_json/'):
        return util.jsonify_model_db(config_db)
    return flask.render_template(
        'admin/config_update.html',
        title=u'Общие настройки',
        html_class='admin-config',
        form=form,
        config_db=config_db,
    )