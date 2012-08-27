# -*- coding: utf-8 -*-
import flask

mod = flask.Blueprint(
    'extras',
    __name__,
    url_prefix='/extras',
    template_folder='templates'
)

mod_json = flask.Blueprint(
    'extras_json',
    __name__,
    url_prefix='/_json/extras'
)

@mod_json.route('/', endpoint='index')
@mod.route('/', endpoint='index')
def extras():
    country = None
    region = None
    city = None
    city_lat_long = None
    if 'X-AppEngine-Country' in flask.request.headers:
        country = flask.request.headers['X-AppEngine-Country']
    if 'X-AppEngine-Region' in flask.request.headers:
        region = flask.request.headers['X-AppEngine-Region']
    if 'X-AppEngine-City' in flask.request.headers:
        city = flask.request.headers['X-AppEngine-City']
    if 'X-AppEngine-CityLatLong' in flask.request.headers:
        city_lat_long = flask.request.headers['X-AppEngine-CityLatLong']

    extra_info = {
        'country': country,
        'region': region,
        'city': city,
        'city_lat_long': city_lat_long,
        'user_agent': flask.request.headers['User-Agent'],
        }

    if flask.request.path.startswith('/_json/'):
        return flask.jsonify(extra_info)

    return flask.render_template(
        'extras/extras.html',
        html_class='extras',
        title='Extras',
        extra_info=extra_info,
    )

_blueprints = (mod, mod_json,)