__author__ = 'Bohdan Mushkevych'

try:
    from http.client import NO_CONTENT
except ImportError:
    from httplib import NO_CONTENT

import json
from werkzeug.wrappers import Response

from synergy.mx.utils import render_template, expose
from flow.mx.flow_action_handler import FlowActionHandler, RUN_MODE_RUN_ONE, RUN_MODE_RUN_FROM


@expose('/flow/details/step/')
def details_flow_step(request, **values):
    details = FlowActionHandler(request, **values)
    return Response(response=json.dumps(details.step_details), mimetype='application/json')


@expose('/flow/details/flow/')
def details_flow(request, **values):
    details = FlowActionHandler(request, **values)
    return Response(response=json.dumps(details.flow_details), mimetype='application/json')


@expose('/flow/action/change_run_mode/')
def action_change_run_mode(request, **values):
    handler = FlowActionHandler(request, **values)
    handler.action_change_run_mode()
    return Response(status=NO_CONTENT)


@expose('/flow/action/run_one_step/')
def action_run_one_step(request, **values):
    handler = FlowActionHandler(request, **values)
    return Response(response=json.dumps(handler.perform_freerun_action(RUN_MODE_RUN_ONE)),
                    mimetype='application/json')


@expose('/flow/action/run_from_step/')
def action_run_from(request, **values):
    handler = FlowActionHandler(request, **values)
    return Response(response=json.dumps(handler.perform_freerun_action(RUN_MODE_RUN_FROM)),
                    mimetype='application/json')


@expose('/flow/action/get_step_log/')
def action_get_step_log(request, **values):
    handler = FlowActionHandler(request, **values)
    return Response(response=json.dumps(handler.action_get_step_log()), mimetype='application/json')


@expose('/flow/action/get_flow_log/')
def action_get_flow_log(request, **values):
    handler = FlowActionHandler(request, **values)
    return Response(response=json.dumps(handler.action_get_flow_log()), mimetype='application/json')


@expose('/viewer/flow/')
def flow_viewer(request, **values):
    details = FlowActionHandler(request, **values)
    return render_template('flow_viewer.html',
                           flow_details=details.flow_details,
                           process_name=details.process_name,
                           active_run_mode=details.active_run_mode)
