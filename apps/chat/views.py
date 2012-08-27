# -*- coding: utf-8 -*-
import flask

mod = flask.Blueprint(
    'chat',
    __name__,
    url_prefix='/chat',
    template_folder='templates'
)

@mod.route('/', endpoint='index')
def chat():
    return flask.render_template(
        'chat/chat.html',
        title='Chat',
        html_class='chat',
        channel_name='chat',
    )

_blueprints = (mod,)