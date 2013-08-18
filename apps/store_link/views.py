# -*- coding: utf-8 -*-
import flask

mod = flask.Blueprint(
    "store_link",
    __name__,
    template_folder='templates'
)
