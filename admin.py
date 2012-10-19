# -*- coding: utf-8 -*-

from flaskext import wtf
from main import app


class ConfigUpdateForm(wtf.Form):
    brand_name = wtf.TextField(
        'Brand Name', [wtf.validators.required()]
    )
    analytics_id = wtf.TextField(
        'Analytics ID', [wtf.validators.optional()]
    )
    facebook_app_id = wtf.TextField(
        'Facebook ID', [wtf.validators.optional()]
    )
    facebook_app_secret = wtf.TextField(
        'Facebook Secret', [wtf.validators.optional()]
    )
    vk_app_id = wtf.TextField(
        'Vkontakte ID', [wtf.validators.optional()]
    )
    vk_app_secret = wtf.TextField(
        'Vkontakte Secret', [wtf.validators.optional()]
    )
    ya_app_id = wtf.TextField(
        'Yandex app ID', [wtf.validators.optional()]
    )
    ya_app_secret = wtf.TextField(
        'Yandex app password', [wtf.validators.optional()]
    )

    mailru_app_id = wtf.TextField(
        'Mail.ru app ID', [wtf.validators.optional()]
    )
    mailru_app_secret = wtf.TextField(
        'Mail.ru secret key', [wtf.validators.optional()]
    )

    odnoklassniki_app_id = wtf.TextField(
        'Odnoklassniki app ID', [wtf.validators.optional()]
    )
    odnoklassniki_app_public = wtf.TextField(
        'Odnoklassniki public key', [wtf.validators.optional()]
    )
    odnoklassniki_app_secret = wtf.TextField(
        'Odnoklassniki secret key', [wtf.validators.optional()]
    )

    twitter_consumer_key = wtf.TextField(
        'Twitter Key', [wtf.validators.optional()]
    )
    twitter_consumer_secret = wtf.TextField(
        'Twitter Secret', [wtf.validators.optional()]
    )

    feedback_email = wtf.TextField('Feedback Email', [
        wtf.validators.optional(),
        wtf.validators.email("That doesn't look like an email"),
    ])

    pubnub_publish = wtf.TextField(
        'PubNub Publish', [wtf.validators.optional()]
    )
    pubnub_subscribe = wtf.TextField(
        'PubNub Subsrcibe', [wtf.validators.optional()]
    )
    pubnub_secret = wtf.TextField(
        'PubNub Secret', [wtf.validators.optional()]
    )
    flask_secret_key = wtf.TextField(
        'Flask Secret Key', [wtf.validators.required()]
    )


def update_config_variables(config_db):
    app.config.update(
        BRAND_NAME=config_db.brand_name,
        ANALYTICS_ID=config_db.analytics_id,
        SECRETE_KEY=config_db.flask_secret_key,
    )
