__author__ = 'Bohdan Mushkevych'

from synergy.mx.base_request_handler import BaseRequestHandler, valid_action_request, safe_json_response
from flow.conf import flows
from flow.db.dao.flow_dao import FlowDao
from flow.db.dao.step_dao import StepDao


class FlowActionHandler(BaseRequestHandler):
    def __init__(self, request, **values):
        super(FlowActionHandler, self).__init__(request, **values)
        self.flow_dao = FlowDao(self.logger)
        self.step_dao = StepDao(self.logger)

        self.flow_name = self.request_arguments.get('flow_name')
        self.step_name = self.request_arguments.get('step_name')
        self.timeperiod = self.request_arguments.get('timeperiod')
        self.is_request_valid = True if self.flow_name and self.timeperiod else False

        if self.is_request_valid:
            self.flow_name = self.flow_name.strip()
            self.timeperiod = self.timeperiod.strip()

    @property
    def flow_entry(self):
        return flows.get(self.flow_name)

    @safe_json_response
    def action_get_flow(self):
        flow_entry = self.flow_dao.get_one([self.flow_name, self.timeperiod]).document
        return flow_entry

    @safe_json_response
    def action_get_step(self):
        resp = self.step_dao.get_one([self.flow_name, self.step_name, self.timeperiod]).document
        return resp

    @valid_action_request
    def action_recover(self):
        pass

    @valid_action_request
    def action_run_one_step(self):
        pass
