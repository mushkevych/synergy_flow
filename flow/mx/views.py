__author__ = 'Bohdan Mushkevych'

try:
    from http.client import NO_CONTENT
except ImportError:
    from httplib import NO_CONTENT

import json
from werkzeug.wrappers import Response

from synergy.mx.utils import render_template, expose
from flow.mx.flow_action_handler import FlowActionHandler, RUN_MODE_RUN_ONE, RUN_MODE_RUN_FROM


# for future use
@expose('/flow/step/details/')
def details_flow_step(request, **values):
    details = FlowActionHandler(request, **values)
    return Response(response=json.dumps(details.step_details), mimetype='application/json')


# for future use
@expose('/flow/flow/details/')
def details_flow(request, **values):
    details = FlowActionHandler(request, **values)
    return Response(response=json.dumps(details.flow_details), mimetype='application/json')


@expose('/flow/run/mode/')
def set_run_mode(request, **values):
    handler = FlowActionHandler(request, **values)
    handler.set_run_mode()
    return Response(status=NO_CONTENT)


@expose('/flow/run/one_step/')
def run_one_step(request, **values):
    handler = FlowActionHandler(request, **values)
    return Response(response=json.dumps(handler.perform_freerun_action(RUN_MODE_RUN_ONE)),
                    mimetype='application/json')


@expose('/flow/run/from_step/')
def run_from_step(request, **values):
    handler = FlowActionHandler(request, **values)
    return Response(response=json.dumps(handler.perform_freerun_action(RUN_MODE_RUN_FROM)),
                    mimetype='application/json')


@expose('/flow/step/log/')
def get_step_log(request, **values):
    handler = FlowActionHandler(request, **values)
    return Response(response=json.dumps(handler.get_step_log()), mimetype='application/json')


@expose('/flow/flow/log/')
def get_flow_log(request, **values):
    handler = FlowActionHandler(request, **values)
    return Response(response=json.dumps(handler.get_flow_log()), mimetype='application/json')


@expose('/viewer/flow/')
def flow_viewer(request, **values):
    handler = FlowActionHandler(request, **values)
    return render_template('flow_viewer.html',
                           flow_details=handler.flow_details,
                           process_name=handler.process_name,
                           active_run_mode=handler.active_run_mode,
                           freerun_uows=handler.freerun_uow_records)
