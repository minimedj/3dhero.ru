# -*- coding: utf-8 -*-

from flask import Blueprint, request, redirect, url_for, render_template, flash
from auth import admin_required
from apps.order.models import PartnerRequest, REQUEST_STATUS
import logging


mod = Blueprint(
    'admin.order',
    __name__,
    template_folder='templates',
    url_prefix='/admin/order'
)

@mod.route('/requests/', methods=['GET'], endpoint='requests')
@admin_required
def get_requests():
    requests = PartnerRequest.query(PartnerRequest.status == REQUEST_STATUS['now'])
    requests_accept = PartnerRequest.query(PartnerRequest.status == REQUEST_STATUS['accept'])
    requests_reject = PartnerRequest.query(PartnerRequest.status == REQUEST_STATUS['reject'])
    requests_admin = PartnerRequest.query(PartnerRequest.status == REQUEST_STATUS['admin'])
    return render_template(
        'admin/order/requests.html',
        requests = requests,
        requests_accept = requests_accept,
        requests_reject = requests_reject,
        requests_admin = requests_admin
    )

@mod.route('/request/<int:key_id>', methods=['GET', 'POST'], endpoint='request')
@admin_required
def get_request(key_id):
    request_obj = PartnerRequest.retrieve_by_id(key_id)
    if not request_obj:
        flash(u'Запрос на регистрацию "%s" не найден' % key_id, category='error')
        return redirect(url_for('admin.order.requests'))
    if not request_obj.customer:
        flash(
            u'Упс, произошла ошибка - профиль пользователя, для запроса "%s", не найден' % key_id,
            category='error'
        )
        logging.error(u'User profile not found (request: %s)' % key_id)
        return redirect(url_for('admin.order.requests'))
    customer = request_obj.customer.get()
    if request.method == 'POST':
        if 'request_accept' in request.form:
            flash(u'Запрос клиента "%s" был одобрен' % customer.name)
            request_obj.status = REQUEST_STATUS['accept']
            request_obj.put()
        if 'request_reject' in request.form:
            flash(u'Запрос клиента "%s" был отклонен' % customer.name)
            request_obj.status = REQUEST_STATUS['reject']
            request_obj.put()
        if 'request_admin' in request.form:
            flash(u'Запрос администратора "%s" был одобрен' % customer.name)
            request_obj.status = REQUEST_STATUS['admin']
            request_obj.put()
        if 'request_reset' in request.form:
            flash(u'Запрос для клиента "%s" был сброшен' % customer.name)
            request_obj.key.delete()
        return redirect(url_for('admin.order.requests'))
    return render_template(
        'admin/order/request.html',
        request_status = request_obj.status,
        customer=customer
    )