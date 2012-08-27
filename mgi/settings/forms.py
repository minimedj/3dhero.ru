from flask.ext import wtf

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
    feedback_email = wtf.TextField('Feedback Email', [
        wtf.validators.optional(),
        wtf.validators.email("That doesn't look like an email"),
        ])
    twitter_consumer_key = wtf.TextField(
        'Twitter Key', [wtf.validators.optional()]
    )
    twitter_consumer_secret = wtf.TextField(
        'Twitter Secret', [wtf.validators.optional()]
    )
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