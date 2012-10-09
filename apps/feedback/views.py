# -*- coding: utf-8 -*-
import flask
from google.appengine.api import mail
from model import Config
from auth import current_user_id, current_user_db
from apps.feedback.forms import FeedbackForm
from apps.feedback.models import Feedback
from apps.manager.models import Manager

mod = flask.Blueprint(
    "feedback",
    __name__,
    url_prefix='/feedback',
    template_folder='templates'
)

@mod.route('/', methods=['GET', 'POST'])
def index():
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback()
        form.populate_obj(feedback)
        feedback.put()
        feedback_email = Config.get_master_db().feedback_email
        managers = Manager.query()
        if feedback_email and managers:
            subject=u'[%s] Сообщение - %s' % (
                    Config.get_master_db().brand_name,
                    form.subject.data,
            )
            body = u'%s\n\n%s' % (form.feedback.data, form.email.data)
            for manager in managers:
                if manager.email:
                    mail.send_mail(
                        sender=Config.get_master_db().feedback_email,
                        to=manager.email,
                        subject=subject,
                        reply_to=form.email.data or Config.get_master_db().feedback_email,
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
    )

_blueprints = (mod,)