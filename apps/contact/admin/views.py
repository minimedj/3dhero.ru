# -*- coding: utf-8 -*-

from flask import Blueprint, request, redirect, url_for, render_template, flash
from auth import admin_required
from apps.contact.models import Contact
from apps.contact.admin.forms import ContactForm
from google.appengine.ext import ndb

mod = Blueprint(
    'admin.contact',
    __name__,
    template_folder='templates',
    url_prefix='/admin/contact'
)

@mod.route('/')
@admin_required
def index():
    contacts = Contact.query().order(-Contact.order_id)
    return render_template(
        'admin/contact/index.html',
        contacts=contacts
    )

def set_geo(form, obj):
    if form.latitude.data and form.longitude.data:
        obj.geo = ndb.GeoPt(lat=form.latitude.data, lon=form.longitude.data)
    else:
        obj.geo = None

def get_geo(obj, form):
    if obj.geo:
        form.latitude.data = obj.geo.lat
        form.longitude.data = obj.geo.lon

@mod.route('/add/', methods=['GET', 'POST'])
@admin_required
def add():
    form = ContactForm()
    if form.validate_on_submit():
        new_contact = Contact()
        form.populate_obj(new_contact)
        set_geo(form, new_contact)
        new_contact.put()
        return redirect(url_for('admin.contact.index'))
    return render_template(
        'admin/contact/add.html',
        form=form
    )

@mod.route('/edit/<int:key_id>', methods=['GET', 'POST'])
@admin_required
def edit(key_id):
    contact = Contact.retrieve_by_id(key_id)
    if not contact:
        flash(u'Не удалось найти указанный контакт "%s"' % key_id, category='error')
        return redirect(url_for('admin.contact.index'))
    if request.method == 'POST' and 'delete_contact' in request.form:
        contact.key.delete()
        flash(u'Контакт удален')
        return redirect(url_for('admin.contact.index'))
    form = ContactForm(obj=contact)
    if request.method == 'GET':
        get_geo(contact, form)
    if form.validate_on_submit():
        form.populate_obj(contact)
        set_geo(form, contact)
        contact.put()
        flash(u'Контакт обновлен', category='success')
        return redirect(url_for('admin.contact.index'))
    return render_template(
        'admin/contact/edit.html',
        form=form
    )