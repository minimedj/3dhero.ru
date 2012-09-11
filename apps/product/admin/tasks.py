# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, url_for
from google.appengine.api import memcache
from google.appengine.api.taskqueue import taskqueue
from google.appengine.ext import ndb, db
from util import uuid
from apps.api.v1.views import model_populate
from apps.product.models import (Product, Category, Genre, Series)
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


@mod.route('/post_put_category/<int:key_id>/<string:mem_key>/', methods=['POST'])
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
        def do_txn():
            product_mem_key = uuid()
            memcache.add(
                product_mem_key,
                {'category':category.name},
                7200
            )
            taskqueue.add(
                url=url_for(
                    'product.task.update_product',
                    key_id=product,
                    mem_key=product_mem_key),
                transactional=True
            )
        db.run_in_transaction(do_txn())
    return jsonify({
        'success': True,
        'msg': 'Complete update of category %s' % category.key.id()
    })

@mod.route('/post_put_genre/<int:key_id>/<string:mem_key>/', methods=['POST'])
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
        def do_txn():
            product_mem_key = uuid()
            memcache.add(
                product_mem_key,
                {'genre':category.name},
                7200
            )
            taskqueue.add(
                url=url_for(
                    'product.task.update_product',
                    key_id=product,
                    mem_key=product_mem_key),
                transactional=True
            )
        db.run_in_transaction(do_txn)
    return jsonify({
        'success': True,
        'msg': 'Complete update of genre %s' % category.key.id()
    })

@mod.route('/post_put_series/<int:key_id>/<string:mem_key>/', methods=['POST'])
def post_put_series(key_id, mem_key):
    res, obj = get_mem_obj(mem_key)
    if not res:
        return obj
    series = Series.retrieve_by_id(key_id)
    if not series:
        return jsonify({
            'success': False,
            'msg': 'Series id:%s not found' % key_id
        })
    for product in series.all_products:
        def do_txn():
            product_mem_key = uuid()
            memcache.add(
                product_mem_key,
                {'series':series.name},
                7200
            )
            taskqueue.add(
                url=url_for(
                'product.task.update_product',
                key_id=product,
                mem_key=product_mem_key),
                transactional=True
            )
        db.run_in_transaction(do_txn)
    return jsonify({
        'success': True,
        'msg': 'Complete update of series %s' % series.key.id()
    })
