# -*- coding: utf-8 -*-
import flask

mod = flask.Blueprint(
    "pages",
    __name__,
    template_folder='templates'
)

@mod.route('/')
def index():
    return flask.render_template(
        'pages/index.html',
        html_class='welcome',
        channel_name='welcome',
    )


_blueprints = (mod,)