# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request
from apps.product.models import Category, Series, Brand
from apps.product.admin.forms import CategoryForm, SeriesForm, BrandForm
from auth import admin_required

mod = Blueprint(
    'admin.product',
    __name__,
    template_folder='templates',
    url_prefix='/admin/product'
)

@mod.route('/categories/', methods=['GET', 'POST'])
@admin_required
def categories():
    categories = Category.query().order(Category.name)
    form = CategoryForm()
    if form.validate_on_submit():
        new_cat = Category()
        form.populate_obj(new_cat)
        new_cat.put()
        return redirect(url_for('admin.product.categories'))
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
        return redirect(url_for('admin.product.categories'))
    form = CategoryForm(obj=category)
    if request.method == 'POST' and 'delete_category' in request.form:
        category.key.delete()
        return redirect(url_for('admin.product.categories'))
    if form.is_submitted() and form.validate(is_edit=True):
        form.populate_obj(category)
        category.put()
        return redirect(url_for('admin.product.categories'))
    return render_template(
        'product/admin/category/edit.html',
        category=category,
        form=form
    )

@mod.route('/series/', methods=['GET', 'POST'])
@admin_required
def series():
    series = Series.query().order(Series.name)
    form = CategoryForm()
    if form.validate_on_submit():
        new_series = Series()
        form.populate_obj(new_series)
        new_series.put()
        return redirect(url_for('admin.product.series'))
    return render_template(
        'product/admin/series/all.html',
        series=series,
        form=form
    )

@mod.route('/series/<int:key_id>/', methods=['GET', 'POST'])
@admin_required
def series_edit(key_id):
    series = Series.retrieve_by_id(key_id)
    if not series:
        return redirect(url_for('admin.product.series'))
    form = SeriesForm(obj=series)
    if request.method == 'POST' and 'delete_series' in request.form:
        series.key.delete()
        return redirect(url_for('admin.product.series'))
    if form.is_submitted() and form.validate(is_edit=True):
        form.populate_obj(series)
        series.put()
        return redirect(url_for('admin.product.series'))
    return render_template(
        'product/admin/series/edit.html',
        series=series,
        form=form
    )

@mod.route('/brands/', methods=['GET', 'POST'])
@admin_required
def brands():
    brands = Brand.query().order(Brand.name)
    form = BrandForm()
    if form.validate_on_submit():
        new_series = Brand()
        form.populate_obj(new_series)
        new_series.put()
        return redirect(url_for('admin.product.brands'))
    return render_template(
        'product/admin/brand/all.html',
        brands=brands,
        form=form
    )

@mod.route('/brands/<int:key_id>/', methods=['GET', 'POST'])
@admin_required
def brand_edit(key_id):
    brand = Brand.retrieve_by_id(key_id)
    if not brand:
        return redirect(url_for('admin.product.brands'))
    form = SeriesForm(obj=brand)
    if request.method == 'POST' and 'delete_brand' in request.form:
        brand.key.delete()
        return redirect(url_for('admin.product.brands'))
    if form.is_submitted() and form.validate(is_edit=True):
        form.populate_obj(brand)
        brand.put()
        return redirect(url_for('admin.product.brands'))
    return render_template(
        'product/admin/brand/edit.html',
        brand=brand,
        form=form
    )

from apps.product.admin.tasks import mod as task_mod
_blueprints = (mod, task_mod,)