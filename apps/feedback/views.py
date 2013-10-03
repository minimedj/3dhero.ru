# -*- coding: utf-8 -*-
import re
import flask
from google.appengine.api import mail
from model import Config
from auth import current_user_id, current_user_db
from apps.feedback.forms import FeedbackForm, FeedbackCaptchaForm
from apps.feedback.models import Feedback
from apps.manager.models import Manager

mod = flask.Blueprint(
    "feedback",
    __name__,
    url_prefix='/feedback',
    template_folder='templates'
)


def collect_emails(text):
    email_pattern = re.compile("[-a-zA-Z0-9._]+@[-a-zA-Z0-9_]+.[a-zA-Z0-9_.]+")
    return re.findall(email_pattern, text)


@mod.route('/', methods=['GET', 'POST'])
def index():
    master_db = Config.get_master_db()
    if master_db.recaptcha_public_key and master_db.recaptcha_private_key:
        if not flask.request.headers.getlist("X-Forwarded-For"):
            ip = flask.request.remote_addr
        else:
            ip = flask.request.headers.getlist("X-Forwarded-For")[0]
        form = FeedbackCaptchaForm(captcha={
            'ip_address': ip,
            'public_key': master_db.recaptcha_public_key,
            'private_key': master_db.recaptcha_private_key
        })
        use_captcha = True
    else:
        form = FeedbackForm()
        use_captcha = False
    if form.validate_on_submit():
        feedback = Feedback()
        form.populate_obj(feedback)
        feedback.put()
        feedback_email = master_db.feedback_email
        managers = Manager.query()
        if feedback_email and managers:
            subject = u'[%s] Сообщение - %s' % (
                master_db.brand_name,
                form.subject.data
            )
            body = u'%s\n\n%s' % (form.feedback.data, form.email.data)
            for manager in managers:
                if manager.email and manager.is_mailable:
                    emails = collect_emails(manager.email)
                    for email in emails:
                        mail.send_mail(
                            sender=master_db.feedback_email,
                            to=email,
                            subject=subject,
                            reply_to=form.email.data or master_db.feedback_email,
                            body=body
                        )
        flask.flash(u'Спасибо за Ваш отзыв!', category='success')
        return flask.redirect(flask.url_for('pages.index'))
    if not form.errors and current_user_id() > 0:
        form.email.data = current_user_db().email
    return flask.render_template(
        'feedback/index.html',
        title=u'Обратная связь',
        html_class='feedback',
        form=form,
        use_captcha=use_captcha
    )

_blueprints = (mod,)
