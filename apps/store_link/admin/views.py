# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request
from apps.store_link.admin.forms import StoreLinkForm
from apps.store_link.models import StoreLink

mod = Blueprint(
    'admin.store_link',
    __name__,
    template_folder='templates',
    url_prefix='/admin/store_link'
)

@mod.route('/', methods=['GET', 'POST'])
def index():
    form = StoreLinkForm()
    if form.validate_on_submit():
        store_link = StoreLink()
        form.populate_obj(store_link)
        store_link.put()
        return redirect(url_for('admin.store_link.index'))
    store_links = StoreLink.query()
    return render_template(
        'admin/store_link/index.html',
        form=form,
        store_links=store_links
    )

@mod.route('/<int:key_id>/delete/', methods=['POST'], endpoint='delete')
def del_link(key_id):
    link = StoreLink.retrieve_by_id(key_id)
    if link and 'delete' in request.form:
        link.key.delete()
    return redirect(url_for('admin.store_link.index'))