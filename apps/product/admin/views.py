# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request
from apps.product.models import Category
from apps.product.admin.forms import CategoryForm
from auth import admin_required

mod = Blueprint(
    'product.admin',
    __name__,
    template_folder='templates',
    url_prefix='/admin/product'
)

@mod.route('/categories/', methods=['GET', 'POST'])
@admin_required
def categories():
    categories = Category.query()
    form = CategoryForm()
    if form.validate_on_submit():
        new_cat = Category()
        form.populate_obj(new_cat)
        new_cat.put()
        return redirect(url_for('product.admin.categories'))
    return render_template(
        'product/admin/category/all.html',
        categories=categories,
        form=form
    )

@mod.route('/categories/<int:key_id>/', methods=['GET', 'POST'])
@admin_required
def category_edit(key_id):
    category = Category.retrieve_by_id(key_id)
    if not category:
        return redirect(url_for('product.admin.categories'))
    form = CategoryForm(obj=category)
    if request.method == 'POST' and 'delete_category' in request.form:
        category.key.delete()
        return redirect(url_for('product.admin.categories'))
    if form.is_submitted() and form.validate(is_edit=True):
        form.populate_obj(category)
        category.put()
        return redirect(url_for('product.admin.categories'))
    return render_template(
        'product/admin/category/edit.html',
        category=category,
        form=form
    )

from apps.product.admin.tasks import mod as task_mod
_blueprints = (mod, task_mod,)