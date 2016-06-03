__author__ = 'Bohdan Mushkevych'

from os import path

from werkzeug.local import Local, LocalManager
from werkzeug.routing import Map, Rule

from synergy.mx import utils

STATIC_FLOW_PATH = path.dirname(__file__)


def register_flow_mx(mx):
    """ function registers lookup path for Synergy Flow context
        :param mx: synergy.mx.synergy_mx.MX instance
    """
    utils.url_map.add(Rule('/flow/static/<file>', endpoint='flow/static', build_only=True))
    mx.exports['flow/static'] = mx.get_directory_loader(STATIC_FLOW_PATH)
