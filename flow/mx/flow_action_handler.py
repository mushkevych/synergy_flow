__author__ = 'Bohdan Mushkevych'

from datetime import datetime

from synergy.conf import settings, context
from synergy.mx.base_request_handler import BaseRequestHandler, valid_action_request
from synergy.db.model import unit_of_work
from synergy.db.model.unit_of_work import UnitOfWork
from werkzeug.utils import cached_property

from flow.conf import flows
from flow.flow_constants import ARGUMENT_FLOW_NAME
from flow.core.execution_context import ExecutionContext
from flow.db.dao.flow_dao import FlowDao
from flow.db.dao.step_dao import StepDao
from flow.mx.rest_model_factory import *


class FlowActionHandler(BaseRequestHandler):
    def __init__(self, request, **values):
        super(FlowActionHandler, self).__init__(request, **values)
        self.flow_dao = FlowDao(self.logger)
        self.step_dao = StepDao(self.logger)

        self.process_name = self.request_arguments.get('process_name')
        self.flow_name = self.request_arguments.get('flow_name')
        if not self.flow_name and self.process_name:
            process_entry = context.process_context[self.process_name]
            self.flow_name = process_entry.arguments.get(ARGUMENT_FLOW_NAME)

        self.step_name = self.request_arguments.get('step_name')
        self.timeperiod = self.request_arguments.get('timeperiod')
        self.is_request_valid = True if self.flow_name \
                                        and self.flow_name in flows.flows \
                                        and self.timeperiod else False

        if self.is_request_valid:
            self.flow_name = self.flow_name.strip()
            self.timeperiod = self.timeperiod.strip()

    @property
    def flow_graph_obj(self):
        _flow_graph_obj = copy.deepcopy(flows.flows[self.flow_name])
        _flow_graph_obj.context = ExecutionContext(self.flow_name, self.timeperiod, None, None, settings.settings)

        try:
            flow_entry = self.flow_dao.get_one([self.flow_name, self.timeperiod])
            _flow_graph_obj.context.flow_entry = flow_entry
            _flow_graph_obj.context.start_timeperiod = flow_entry.start_timeperiod
            _flow_graph_obj.context.end_timeperiod = flow_entry.end_timeperiod

            steps = self.step_dao.get_all_by_flow_id(flow_entry.db_id)
            for s in steps:
                assert isinstance(s, Step)
                _flow_graph_obj[s.step_name].step_entry = s
                _flow_graph_obj.yielded.append(s)
        except LookupError:
            pass
        return _flow_graph_obj

    @cached_property
    @valid_action_request
    def flow_details(self):
        rest_model = create_rest_flow(self.flow_graph_obj)
        return rest_model.document

    @cached_property
    def process_name(self):
        return self.process_name

    @cached_property
    @valid_action_request
    def step_details(self):
        graph_node_obj = self.flow_graph_obj._dict[self.step_name]
        rest_model = create_rest_step(graph_node_obj)
        return rest_model.document

    def _submit_mq_request(self, process_name, step_name, run_mode):
        uow = UnitOfWork()
        uow.process_name = process_name
        uow.timeperiod = self.flow_graph_obj.timeperiod
        uow.start_timeperiod = self.flow_graph_obj.start_timeperiod
        uow.end_timeperiod = self.flow_graph_obj.end_timeperiod
        uow.submitted_at = datetime.utcnow()
        uow.source = context.process_context[process_name].source
        uow.sink = context.process_context[process_name].sink
        uow.state = unit_of_work.STATE_REQUESTED
        uow.unit_of_work_type = unit_of_work.TYPE_MANAGED
        uow.number_of_retries = 0
        uow.arguments = context.process_context[process_name].arguments
        uow.db_id = self.uow_dao.insert(uow)

        msg = 'SynergyCreated: UOW {0} for {1}@{2}.'.format(uow.db_id, process_name, start_timeperiod)
        self._log_message(INFO, process_name, start_timeperiod, msg)
        return uow

    @valid_action_request
    def action_recover(self):
        """
        - create UOW with appropriate run mode
        - locate appropriate Queue for given process
        - submit UOW
        """
        pass

    @valid_action_request
    def action_run_one_step(self):
        pass

    @valid_action_request
    def action_get_step_log(self):
        pass
