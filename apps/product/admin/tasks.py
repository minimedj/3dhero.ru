# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from google.appengine.api import memcache
from google.appengine.ext import ndb
from apps.api.v1.views import model_populate
from apps.product.models import Product
import logging

mod = Blueprint(
    'product.task',
    __name__,
    url_prefix='/_task'
)

def get_mem_obj(mem_key):
    mem_obj = memcache.get(mem_key)
    if mem_obj is None:
        msg = 'Memcache object %s not found' % mem_key
        logging.error(msg)
        return False, jsonify({
            'success': False,
            'msg': msg
        })
    memcache.delete(mem_key)
    if type(mem_obj) != dict:
        msg = 'Invalid memcache obj: %s' % mem_obj
        logging.error(msg)
        return False, jsonify({
            'success': False,
            'msg': msg
        })
    return True, mem_obj


@mod.route('/update_product/<int:key_id>/<string:mem_key>/', methods=['POST'])
@ndb.toplevel
def update_product(key_id, mem_key):
    res, obj = get_mem_obj(mem_key)
    if not res:
        return obj
    product = Product.retrieve_by_id(key_id)
    if not product:
        return jsonify({
            'success': False,
            'msg': 'Product id:%s not found' % key_id
        })
    model_populate(obj, product)
    product.put_async()
    return jsonify({
        'success': True,
        'msg': 'Complete update of product'
    })
