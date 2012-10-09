# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for
from auth import admin_required
import util
from model import User

mod = Blueprint(
    'admin.user',
    __name__,
    url_prefix='/admin/user',
    template_folder='templates'
)

mod_json = Blueprint(
    'admin.user.json',
    __name__,
    url_prefix='/_json'
)

@mod.route('/')
@mod_json.route('/admin/user/')
@admin_required
def index():
    user_dbs, more_cursor = util.retrieve_dbs(
        User,
        User.query(),
        limit=util.param('limit', int),
        cursor=util.param('cursor'),
        order=util.param('order'),
        name=util.param('name'),
      )

    if request.path.startswith('/_json/'):
        return util.jsonify_model_dbs(user_dbs, more_cursor)
    return render_template(
        'admin/user/index.html',
        title=u'Пользователи',
        user_dbs=user_dbs,
        more_url=util.generate_more_url(more_cursor)
    )