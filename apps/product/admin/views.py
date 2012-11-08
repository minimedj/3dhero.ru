# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request
from apps.product.models import Category, Series, Brand, Product, ProductImage
from apps.product.admin.forms import CategoryForm, SeriesForm, BrandForm, ProductForm, AddImageForm
from auth import admin_required
from google.appengine.api import blobstore
from apps.utils.blobstore import get_uploads
import os

mod = Blueprint(
    'admin.product',
    __name__,
    template_folder='templates',
    url_prefix='/admin/product'
)

@mod.route('/edit/<int:key_id>/', methods=['GET', 'POST'])
@admin_required
def edit(key_id):
    product = Product.retrieve_by_id(key_id)
    if not product:
        return redirect(url_for('admin.config_update'))
    if request.method == 'POST' and 'delete_product' in request.form:
        category = None
        if product.category:
            category = Category.exist(product.category)
        product.key.delete()
        if category:
            return redirect(url_for('pages.category', key_id=category.key.id()))
        else:
            return redirect('pages.catalogue')
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        form.populate_obj(product)
        product.put()
        if 'edit_images' in request.form:
            return redirect(url_for('admin.product.edit_images', key_id=key_id))
        return redirect(url_for('product.get_product', key_id=key_id))
    return render_template(
        'product/admin/edit.html',
        product=product,
        form=form
    )

@mod.route('/edit/<int:key_id>/images/', methods=['GET', 'POST'])
@admin_required
def edit_images(key_id):
    product = Product.retrieve_by_id(key_id)
    if not product:
        return redirect('pages.catalogue')
    form = AddImageForm()
    add_img_url = blobstore.create_upload_url(url_for('admin.product.add_image', key_id=key_id))
    return render_template(
        'product/admin/images_edit.html',
        product=product,
        form=form,
        add_img_url=add_img_url
    )

@mod.route('/edit/<int:key_id>/image/add/', methods=['POST'])
@admin_required
def add_image(key_id):
    product = Product.retrieve_by_id(key_id)
    if not product:
        return redirect('pages.catalogue')

    upload_files = get_uploads(request, 'image')
    if len(upload_files):
        blob_info = upload_files[0]
        if blob_info.size and ProductImage.is_image_type(blob_info.content_type):
            img = ProductImage.create(
                blob_info.key(),
                size=blob_info.size,
                filename=os.path.basename(blob_info.filename.replace('\\','/')),
                content_type=blob_info.content_type)
            if not len(product.images_list):
                img.is_master = True
            if img.get_cached_url():
                product.images_list.append(img)
                product.put()
        else:
            blob_info.delete()
    return redirect(url_for('admin.product.edit_images', key_id=key_id))

@mod.route('/edit/<int:key_id>/image/<string:img_uid>/delete/', methods=['POST'])
@admin_required
def delete_image(key_id, img_uid):
    product = Product.retrieve_by_id(key_id)
    if not product:
        return redirect(url_for('admin.product.edit', key_id=key_id))
    for i, img in enumerate(product.images_list):
        if img.uid == img_uid:
            img.delete_blob()
            del product.images_list[i]
            product.put()
            break
    return redirect(url_for('admin.product.edit_images', key_id=key_id))

@mod.route('/edit/<int:key_id>/image/<string:img_uid>/default/', methods=['POST'])
@admin_required
def default_image(key_id, img_uid):
    product = Product.retrieve_by_id(key_id)
    if not product:
        return redirect(url_for('admin.product.edit', key_id=key_id))
    for i, img in enumerate(product.images_list):
        if img.uid == img_uid:
            product.images_list[0], product.images_list[i] = \
            product.images_list[i], product.images_list[0]
            product.put()
            break
    return redirect(url_for('admin.product.edit_images', key_id=key_id))

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