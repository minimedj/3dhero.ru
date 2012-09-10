# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, url_for
from google.appengine.api import memcache, taskqueue
from google.appengine.ext import ndb
from util import uuid
from apps.api.v1.views import model_populate
from apps.product.models import (Product, Category, Genre, Series)

mod = Blueprint(
    'product.tasks',
    __name__,
    url_prefix='/_task'
)

def get_mem_obj(mem_key):
    mem_obj = memcache.get(mem_key)
    if not mem_obj:
        False, jsonify({
            'success': False,
            'msg': 'Memcache object %s not found' % mem_key
        })
    memcache.delete(mem_key)
    if type(mem_obj) != dict:
        return False, jsonify({
            'success': False,
            'msg': 'Invalid memcache obj: %s' % mem_obj
        })
    return True, mem_obj


@mod.route('/update_product/<int:key_id>/<string:mem_key>/')
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


@mod.route('/post_put_category/<int:key_id>/<string:mem_key>/')
def post_put_category(key_id, mem_key):
    res, obj = get_mem_obj(mem_key)
    if not res:
        return obj
    category = Category.retrieve_by_id(key_id)
    if not category:
        return jsonify({
            'success': False,
            'msg': 'Category id:%s not found' % key_id
        })
    for product in category.all_products:
        mem_key = uuid()
        memcache.add(
            mem_key,
            {'category':category.name},
            7200
        )
        taskqueue.add(
            url_for(
                'product.admin.update_product',
                key_id=product,
                mem_key=mem_key)
        )
    return jsonify({
        'success': True,
        'msg': 'Complete update of category %s' % category.key.id()
    })

@mod.route('/post_put_genre/<int:key_id>/<string:mem_key>/')
def post_put_genre(key_id, mem_key):
    res, obj = get_mem_obj(mem_key)
    if not res:
        return obj
    category = Genre.retrieve_by_id(key_id)
    if not category:
        return jsonify({
            'success': False,
            'msg': 'Genre id:%s not found' % key_id
        })
    for product in category.all_products:
        mem_key = uuid()
        memcache.add(
            mem_key,
            {'genre':category.name},
            7200
        )
        taskqueue.add(
            url_for(
                'product.admin.update_product',
                key_id=product,
                mem_key=mem_key)
        )
    return jsonify({
        'success': True,
        'msg': 'Complete update of genre %s' % category.key.id()
    })

@mod.route('/post_put_series/<int:key_id>/<string:mem_key>/')
def post_put_genre(key_id, mem_key):
    res, obj = get_mem_obj(mem_key)
    if not res:
        return obj
    category = Series.retrieve_by_id(key_id)
    if not category:
        return jsonify({
            'success': False,
            'msg': 'Series id:%s not found' % key_id
        })
    for product in category.all_products:
        mem_key = uuid()
        memcache.add(
            mem_key,
            {'series':category.name},
            7200
        )
        taskqueue.add(
            url_for(
                'product.admin.update_product',
                key_id=product,
                mem_key=mem_key)
        )
    return jsonify({
        'success': True,
        'msg': 'Complete update of series %s' % category.key.id()
    })
