# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, redirect, url_for
from auth import admin_required
from apps.price.models import PriceFile
from apps.file.models import File
from apps.price.admin.forms import PriceFileForm
from apps.utils.blobstore import get_uploads
from google.appengine.ext import blobstore
import os

mod = Blueprint(
    'admin.price',
    __name__,
    url_prefix='/admin/price',
    template_folder='templates'
)

@mod.route('/')
@admin_required
def index():
    prices = PriceFile.query().order(-PriceFile.order_id)
    form = PriceFileForm()
    if form.validate_on_submit():
        pass
    return render_template(
        'admin/price/index.html',
        prices=prices,
        form=form,
        upload_url=blobstore.create_upload_url(url_for('admin.price.upload_price'))
    )

@mod.route('/<int:key_id>/delete/', methods=['POST'], endpoint='delete')
@admin_required
def price_delete(key_id):
    price = PriceFile.retrieve_by_id(key_id)
    if price and 'delete_price' in request.form:
        price.key.delete()
    return redirect(url_for('admin.price.index'))

@mod.route('/upload_price/', methods=['POST'])
@admin_required
def upload_price():
    form = PriceFileForm()
    if request.method == 'POST' and form.validate_on_submit():
        upload_files = get_uploads(request, 'attach_file_')
        if len(upload_files):
            blob_info = upload_files[0]
            if blob_info.size:
                price_file = PriceFile()
                form.populate_obj(price_file)
                file_ = File.create(
                    blob_info.key(),
                    size=blob_info.size,
                    filename=os.path.basename(blob_info.filename.replace('\\','/')),
                    content_type=blob_info.content_type,
                    is_public=True,
                    description = form.description.data
                )
                file_.put()
                price_file.file = file_.key
                price_file.put()
            else:
                blob_info.delete()
        return redirect(url_for('admin.price.index'))
    prices = PriceFile.query().order(-PriceFile.order_id)
    return render_template(
        'admin/price/index.html',
        prices=prices,
        form=form,
        upload_url=blobstore.create_upload_url(url_for('admin.price.upload_price'))
    )