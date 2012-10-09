# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from flask import render_template
from model import Base
from apps.product.models import Product
from model import User, Config
from google.appengine.api import mail
from apps.manager.models import Manager
import sys

class Order(Base):
    products = ndb.KeyProperty(Product, repeated=True)
    customer = ndb.KeyProperty(User)
    price = ndb.IntegerProperty(verbose_name=u'Сумма на момент заказа')

REQUEST_STATUS = {
    'now': 0,
    'accept': 1,
    'reject': 2,
    'admin': 3
}

class PartnerRequest(Base):
    customer = ndb.KeyProperty(User)
    status = ndb.IntegerProperty(default=REQUEST_STATUS['now'])
    manager_comment = ndb.TextProperty()

    def _post_put_hook(self, future):
        customer = self.customer.get()
        feedback_email = Config.get_master_db().feedback_email
        if customer:
            if self.status == REQUEST_STATUS['accept']:
                customer.is_customer = True
                customer.put()
                if feedback_email and customer.email:
                    mail.send_mail(
                        sender=feedback_email,
                        to=customer.email,
                        subject=u'[%s] - Ваш запрос одобрен' % (
                            Config.get_master_db().brand_name
                        ),
                        body=render_template(
                            'order/emails/customer_request_accept.html',
                            comment = self.manager_comment
                        )
                    )
            if self.status == REQUEST_STATUS['reject']:
                customer.is_customer = False
                customer.put()
                if feedback_email and customer.email:
                    mail.send_mail(
                        sender=feedback_email,
                        to=customer.email,
                        subject=u'[%s] - Ваш запрос отклонен' % (
                            Config.get_master_db().brand_name
                        ),
                        body=render_template(
                            'order/emails/customer_request_reject.html',
                            comment = self.manager_comment
                        )
                    )

            if self.status == REQUEST_STATUS['admin']:
                customer.admin = True
                customer.is_customer = True
                customer.put()
                if feedback_email and customer.email:
                    mail.send_mail(
                        sender=feedback_email,
                        to=customer.email,
                        subject=u'[%s] - Вы - администратор' % (
                            Config.get_master_db().brand_name
                        ),
                        body=render_template(
                            'order/emails/customer_request_admin.html',
                            comment = self.manager_comment
                        )
                    )
            if self.status == REQUEST_STATUS['now']:
                if feedback_email:
                    managers = Manager.query()
                    for manager in managers:
                        if manager.email:
                            mail.send_mail(
                                sender=feedback_email,
                                to=manager.email,
                                subject=u'[%s] - Новый запрос на сотрудничество' % (
                                    Config.get_master_db().brand_name
                                ),
                                body=render_template(
                                    'order/emails/customer_request.html',
                                    customer_request = self,
                                    customer = self.customer.get()
                                )
                            )

    @classmethod
    def _pre_delete_hook(cls, key):
        customer_request = key.get()
        if customer_request and customer_request.customer:
            feedback_email = Config.get_master_db().feedback_email
            customer = customer_request.customer.get()
            if customer.email and feedback_email:
                mail.send_mail(
                    sender=feedback_email,
                    to=customer.email,
                    subject=u'[%s] - Ваш запрос на сотрудничество был сброшен' % (
                        Config.get_master_db().brand_name
                    ),
                    body=render_template(
                        'order/emails/customer_request_reset.html'
                    )
                )