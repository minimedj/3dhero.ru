# -*- coding: utf-8 -*-

from flask import Blueprint, redirect, render_template, url_for, flash, request
from apps.manager.models import Manager
from apps.manager.admin.forms import ManagerForm
from auth import admin_required

mod = Blueprint(
    'admin.manager',
    __name__,
    template_folder='templates',
    url_prefix='/admin/manager'
)

@mod.route('/')
@admin_required
def index():
    managers = Manager.query()
    return render_template(
        'admin/manager/index.html',
        managers = managers
    )

@mod.route('/add/', methods=['GET', 'POST'])
@admin_required
def add():
    form = ManagerForm()
    if form.validate_on_submit():
        manager = Manager()
        form.populate_obj(manager)
        manager.put()
        return redirect(url_for('admin.manager.index'))
    return render_template(
        'admin//manager/add.html',
        form = form
    )

@mod.route('/edit/<int:key_id>/', methods=['GET', 'POST'])
@admin_required
def edit(key_id):
    manager = Manager.retrieve_by_id(key_id)
    if not manager:
        flash(u'Не удалось найти указанного мененджера', category='error')
        return redirect(url_for('admin.manager.index'))
    if request.method == 'POST' and 'delete_manager' in request.form:
        flash(u'Менеджер "%s" удален' % manager.name)
        manager.key.delete()
        return redirect(url_for('admin.manager.index'))
    form = ManagerForm(obj=manager)
    if form.validate_on_submit():
        form.populate_obj(manager)
        manager.put()
        flash(u'Данные мененджера "%s" успешно обновлены' % manager.name, category='success')
        return redirect(url_for('admin.manager.index'))
    return render_template(
        'admin/manager/edit.html',
        form =form
    )