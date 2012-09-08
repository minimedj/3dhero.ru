# -*- coding: utf-8 -*-
import flask
from google.appengine.api import mail
from model import Config
from auth import current_user_id, current_user_db
from apps.feedback.forms import FeedbackForm

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
        mail.send_mail(
            sender=Config.get_master_db().feedback_email,
            to=Config.get_master_db().feedback_email,
            subject='[%s] %s' % (
                Config.get_master_db().brand_name,
                form.subject.data,
                ),
            reply_to=form.email.data or Config.get_master_db().feedback_email,
            body='%s\n\n%s' % (form.feedback.data, form.email.data)
        )
        flask.flash('Thank you for your feedback!', category='success')
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