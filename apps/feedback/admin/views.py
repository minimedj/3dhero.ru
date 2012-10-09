# -*- coding: utf-8 -*-

from flask import Blueprint, redirect, url_for, render_template, request
from auth import admin_required
from apps.feedback.models import Feedback

mod = Blueprint(
    'admin.feedback',
    __name__,
    url_prefix='/admin/feedback',
    template_folder='templates'
)

@mod.route('/')
@admin_required
def index():
    feedbacks = Feedback.query().order(-Feedback.created)
    return render_template(
        'admin/feedback/index.html',
        feedbacks=feedbacks
    )

@mod.route('/<int:key_id>/', methods=['GET', 'POST'], endpoint='view')
def view_feedback(key_id):
    feedback = Feedback.retrieve_by_id(key_id)
    if not feedback:
        return redirect(url_for('admin.feedback.index'))
    if request.method == 'POST' and 'delete_feedback' in request.form:
        feedback.key.delete()
        return redirect(url_for('admin.feedback.index'))
    return render_template(
        'admin/feedback/view.html',
        feedback=feedback
    )
