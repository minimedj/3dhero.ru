# -*- coding: utf-8 -*-

from flask import Blueprint, render_template
from apps.price.models import PriceFile

mod = Blueprint(
    'price',
    __name__,
    template_folder='templates',
    url_prefix='/price'
)

@mod.route('/')
def index():
    prices = PriceFile.query().order(-PriceFile.order_id)
    return render_template(
        'price/index.html',
        prices=prices
    )
