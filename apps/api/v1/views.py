# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from apps.api.v1.models import WriteKey
from apps.api.v1.forms import WriteKeyForm
from util import jsonify_model_dbs, jsonify_model_db, param
from apps.product.models import Product, ProductImage
from functools import wraps
import json, logging
from datetime import datetime
from auth import admin_required
from google.appengine.ext import blobstore
from apps.utils.blobstore import get_uploads
import os

admin_mod = Blueprint(
    'api.v1.admin',
    __name__,
    url_prefix='/admin/api/v1',
    template_folder='templates'
)


@admin_mod.route('/', methods=['GET', 'POST'])
@admin_required
def keys():
    form = WriteKeyForm()
    if request.method == 'POST':
        wk = WriteKey()
        form.populate_obj(wk)
        wk.put()
        return redirect(url_for('api.v1.admin.keys'))
    keys = WriteKey.query()
    return render_template(
        'api/v1/admin/keys.html',
        form=form,
        keys=keys
    )


mod = Blueprint(
    'api.v1',
    __name__,
    url_prefix='/api/v1',
    template_folder='templates'
)


@mod.route('/products', methods=['GET'])
def products():
    products = Product.query()
    return jsonify_model_dbs(products)

@mod.route('/products/<int:key_id>', methods=['GET', 'DELETE', 'PUT'])
def get_product(key_id):
    product = Product.retrieve_by_id(key_id)
    if not product:
        return jsonify({
                'success': False,
                'msg': 'Product with id:%s not found.' % key_id
            })

    if request.method == 'DELETE':
        @check_write_permission
        def delete_product():
            product.key.delete()
            return jsonify({
                'success': True,
                'msg': 'Product id:%s deleted' % key_id
            })
        return delete_product()

    if request.method == 'PUT':
        @check_write_permission
        def put_product():
            flag, model = load_data()
            if not flag:
                return model
            product.clear_sections()
            model_populate(model, product)
            product.put()
            return jsonify({
                'success': True,
                'msg': 'Product has been updated.'
            })
        return put_product()
    return jsonify_model_db(product)


def check_write_permission(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        denied = {'success': False, 'msg': 'Write permission denied.'}
        api_key = param('api_key')
        if not api_key:
            return jsonify(denied)
        key = WriteKey.query(WriteKey.api_key == api_key)
        if not key.count():
            return jsonify(denied)
        return func(*args, **kwargs)
    return wrapped

def except_wrap(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            res = {'success': False,
                   'msg': str(e),
                   'function': func.__name__}
            logging.error(res)
            return jsonify(res, status=400)
    return wrapped

def load_data():
    data = json.loads(request.data)
    if type(data) is not dict:
        return False, jsonify({
            'success': False,
            'msg': 'Invalid model (not dict).',
            'data': data
        }, status=500)

    model = data.get('model')
    if not model:
        return False, jsonify({
            'success': False,
            'msg': 'Model not found',
            'data': data
        }, status=500)
    return True, model

def model_populate(model, product):
    for key in model.keys():
        value = model.get(key)
        if value is None:
            continue
        if key == 'receipt_date':
            try:
                new_date = datetime.date(datetime.strptime(value, '%Y-%m-%d'))
                product.receipt_date = new_date
            except ValueError:
                model.receipt_date = None
            continue
        setattr(product, key, value)


@mod.route('/products/new', methods=['POST'])
@check_write_permission
@except_wrap
def product_new():
    if request.method == 'POST':
        flag, model = load_data()
        if not flag:
            return model
        product = Product()
        model_populate(model, product)
        product.put()
    return jsonify({'success': True})

@mod.route('/products/<int:key_id>/upload_image_url', methods=['POST'])
@check_write_permission
@except_wrap
def product_upload_image_url(key_id):
    url = blobstore.create_upload_url(
        url_for(
            'api.v1.product_upload_image',
            key_id=key_id
        ))
    return jsonify({
        'success': True,
        'upload_url': url
    })

@mod.route('/products/<int:key_id>/upload_image', methods=['POST'])
@except_wrap
def product_upload_image(key_id):
    product = Product.retrieve_by_id(key_id)
    if not product:
       return jsonify({
           'success': False,
           'msg': 'Product id:%s not found' % key_id
       })

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
    else:
        return jsonify({
            'success': False,
            'msg': 'Upload image not found.'
        })
    return jsonify({
        'success': True,
        'msg': 'Upload image complete.'
    })

_blueprints = (admin_mod, mod)
