__author__ = 'Bohdan Mushkevych'

try:
    from http.client import NO_CONTENT
except ImportError:
    from httplib import NO_CONTENT

import json
from werkzeug.wrappers import Response
from werkzeug.utils import redirect

from synergy.mx.gc_action_handler import GcActionHandler
from synergy.mx.freerun_action_handler import FreerunActionHandler
from synergy.mx.managed_action_handler import ManagedActionHandler
from synergy.mx.scheduler_entries import SchedulerEntries
from synergy.mx.dashboard_handler import DashboardHandler
from synergy.mx.utils import render_template, expose
from synergy.mx.tree_node_details import TreeNodeDetails
from synergy.mx.tree_details import TreeDetails


@expose('/details/step/')
def details_flow_step(request, **values):
    details = TreeNodeDetails(request, **values)
    return Response(response=json.dumps(details.details), mimetype='application/json')


@expose('/details/flow/')
def details_flow(request, **values):
    details = TreeDetails(request, **values)
    return Response(response=json.dumps(details.tree_details), mimetype='application/json')


@expose('/action/flow_recover/')
def action_flow_recover(request, **values):
    handler = FreerunActionHandler(request, **values)
    handler.action_update_entry()
    return Response(status=NO_CONTENT)


@expose('/action/reprocess/')
def action_reprocess(request, **values):
    handler = ManagedActionHandler(request, **values)
    handler.action_reprocess()
    return Response(status=NO_CONTENT)


@expose('/action/skip/')
def action_skip(request, **values):
    handler = ManagedActionHandler(request, **values)
    handler.action_skip()
    return Response(status=NO_CONTENT)


@expose('/action/cancel_uow/')
def action_cancel_uow(request, **values):
    handler = FreerunActionHandler(request, **values)
    handler.action_cancel_uow()
    return Response(status=NO_CONTENT)


@expose('/action/get_uow/')
def action_get_uow(request, **values):
    handler = get_action_handler(request, **values)
    return Response(response=json.dumps(handler.action_get_uow()), mimetype='application/json')


@expose('/action/get_event_log/')
def action_get_event_log(request, **values):
    handler = get_action_handler(request, **values)
    return Response(response=json.dumps(handler.action_get_event_log()), mimetype='application/json')


@expose('/action/get_uow_log/')
def action_get_uow_log(request, **values):
    handler = get_action_handler(request, **values)
    return Response(response=json.dumps(handler.action_get_uow_log()), mimetype='application/json')


@expose('/action/change_interval/')
def action_change_interval(request, **values):
    handler = get_action_handler(request, **values)
    handler.action_change_interval()
    return Response(status=NO_CONTENT)


@expose('/action/trigger_now/')
def action_trigger_now(request, **values):
    handler = get_action_handler(request, **values)
    handler.action_trigger_now()
    return Response(status=NO_CONTENT)


@expose('/action/deactivate_trigger/')
def action_deactivate_trigger(request, **values):
    handler = get_action_handler(request, **values)
    handler.action_deactivate_trigger()
    return Response(status=NO_CONTENT)


@expose('/action/activate_trigger/')
def action_activate_trigger(request, **values):
    handler = get_action_handler(request, **values)
    handler.action_activate_trigger()
    return Response(status=NO_CONTENT)


@expose('/gc/flush_all/')
def gc_flush_all(request, **values):
    handler = GcActionHandler(request, **values)
    handler.action_flush_all()
    return Response(status=NO_CONTENT)


@expose('/gc/flush_one/')
def gc_flush_one(request, **values):
    handler = GcActionHandler(request, **values)
    handler.action_flush_one()
    return Response(status=NO_CONTENT)


@expose('/gc/refresh/')
def gc_refresh(request, **values):
    handler = GcActionHandler(request, **values)
    handler.action_refresh()
    return Response(status=NO_CONTENT)


def get_action_handler(request, **values):
    if 'is_freerun' in request.args and request.args['is_freerun'] in ('True', 'true', '1'):
        handler = FreerunActionHandler(request, **values)
    else:
        handler = ManagedActionHandler(request, **values)
    return handler


@expose('/viewer/flow/')
def flow_viewer(request, **values):
    details = TreeDetails(request, **values)
    return render_template('flow_viewer.html', details=details.mx_page_entries)
