__author__ = 'Bohdan Mushkevych'

import json
from os import path
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from werkzeug.local import Local, LocalManager
from werkzeug.wrappers import Response
from werkzeug.routing import Map, Rule

from synergy.conf import context
from synergy.conf import settings
from synergy.mx import utils

STATIC_FLOW_PATH = path.dirname(__file__)

local = Local()
local_manager = LocalManager([local])

# Synergy MX map of URL routing
url_map = Map([Rule('/static_flow/<file>', endpoint='static_flow', build_only=True)])


def register_flow_mx(mx):
    mx.dispath = SharedDataMiddleware(mx.dispatch, {
        '/static_flow': STATIC_FLOW_PATH
    })

    utils.url_map.add()
