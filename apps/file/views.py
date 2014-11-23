# -*- coding: utf-8 -*-

import urllib
from flask import Blueprint, render_template, redirect, url_for
from apps.utils.blobstore import send_blob
from auth import current_user_db, current_user_key, is_logged_in
from apps.file.models import File
from google.appengine.ext import blobstore


mod = Blueprint(
    'file',
    __name__,
    url_prefix='/f',
    template_folder='templates'
)


def _check_owner(file_):
    return file_.is_public \
        or (is_logged_in() and (current_user_db().admin
                                or current_user_key() == file_.owner))


@mod.route('/<string:file_key>', methods=['GET'], endpoint='get')
def get_file(file_key):
    file_ = File.query(File.uid == file_key).get()
    if not file_ or not file_.blob_key:
        return render_template('file/not_found.html')
    if file_.title_filename:
        return redirect(
            url_for(
                'file.get_w_name', file_key=file_key, name=file_.title_filename)
        )
    if not _check_owner(file_):
            return render_template('file/is_private.html')
    return send_blob(file_.blob_key, content_type=file_.content_type)


def get_file_by_uid(cls, uid, check_private=True):
    file_ = cls.query(cls.uid == uid).get()
    if not file_ or not file_.blob_key:
        return render_template('file/not_found.html')
    if check_private and not _check_owner(file_):
        return render_template('file/is_private.html')
    return send_blob(file_.blob_key, content_type=file_.content_type)


@mod.route(
    '/<string:file_key>/<string:name>', methods=['GET'], endpoint='get_w_name')
def get_file_w_name(file_key, name):
    return get_file_by_uid(File, file_key)


@mod.route(
    '/b/<string:blob_key>/<string:name>',
    methods=['GET'],
    endpoint='get_b_w_name')
def get_blob_w_name(blob_key, name):
    blob_key = str(urllib.unquote(blob_key))
    blob_info = blobstore.BlobInfo.get(blob_key)
    return send_blob(blob_info)

_blueprints = (mod,)