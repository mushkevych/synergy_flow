__author__ = 'Bohdan Mushkevych'

from synergy.conf import settings, context
from synergy.db.dao.log_recording_dao import LogRecordingDao
from synergy.db.model.freerun_process_entry import freerun_context_entry
from synergy.mx.base_request_handler import BaseRequestHandler, valid_action_request, safe_json_response
from synergy.scheduler.scheduler_constants import STATE_MACHINE_FREERUN
from synergy.system import time_helper
from werkzeug.utils import cached_property

from flow.conf import flows
from flow.core.execution_context import ExecutionContext
from flow.db.dao.flow_dao import FlowDao
from flow.db.dao.step_dao import StepDao
from flow.flow_constants import *
from flow.mx.rest_model_factory import *


RESPONSE_OK = {'response': 'OK'}
RESPONSE_NOT_OK = {'response': 'Job is not finished'}


class FlowRequest(object):
    def __init__(self, process_name, flow_name, step_name, run_mode, timeperiod, start_timeperiod, end_timeperiod):
        self.process_name = process_name
        self.flow_name = flow_name
        self.step_name = step_name
        self.run_mode = run_mode
        self.timeperiod = timeperiod
        self.start_timeperiod = start_timeperiod
        self.end_timeperiod = end_timeperiod

    @property
    def schedulable_name(self):
        return '{0}::{1}::{2}'.format(self.process_name, self.flow_name, self.step_name)

    @property
    def arguments(self):
        return {
            ARGUMENT_FLOW_NAME: self.flow_name,
            ARGUMENT_STEP_NAME: self.step_name,
            ARGUMENT_RUN_MODE: self.run_mode
        }


class FlowActionHandler(BaseRequestHandler):
    def __init__(self, request, **values):
        super(FlowActionHandler, self).__init__(request, **values)
        self.flow_dao = FlowDao(self.logger)
        self.step_dao = StepDao(self.logger)
        self.log_recording_dao = LogRecordingDao(self.logger)

        self.process_name = self.request_arguments.get(ARGUMENT_PROCESS_NAME)
        self.flow_name = self.request_arguments.get(ARGUMENT_FLOW_NAME)
        if not self.flow_name and self.process_name:
            process_entry = context.process_context[self.process_name]
            self.flow_name = process_entry.arguments.get(ARGUMENT_FLOW_NAME)

        self.step_name = self.request_arguments.get(ARGUMENT_STEP_NAME)
        self.timeperiod = self.request_arguments.get(ARGUMENT_TIMEPERIOD)
        self.start_timeperiod = self.request_arguments.get(ARGUMENT_START_TIMEPERIOD)
        self.end_timeperiod = self.request_arguments.get(ARGUMENT_END_TIMEPERIOD)
        self.is_request_valid = True if self.flow_name \
                                        and self.flow_name in flows.flows \
                                        and self.timeperiod \
                                        and self.start_timeperiod \
                                        and self.end_timeperiod \
            else False

        if self.is_request_valid:
            self.flow_name = self.flow_name.strip()
            self.timeperiod = self.timeperiod.strip()

    def _get_tree_node(self):
        tree = self.scheduler.timetable.get_tree(self.process_name)
        if tree is None:
            raise UserWarning('No Timetable tree is registered for process {0}'.format(self.process_name))

        time_qualifier = context.process_context[self.process_name].time_qualifier
        self.timeperiod = time_helper.cast_to_time_qualifier(time_qualifier, self.timeperiod)
        node = tree.get_node(self.process_name, self.timeperiod)
        return node

    @property
    def job_record(self):
        node = self._get_tree_node()
        return node.job_record

    @property
    def freerun_process_entry(self):
        entry_name = '{0}::{1}'.format(self.flow_name, self.step_name)
        classname = context.process_context[self.process_name].classname
        return freerun_context_entry(
            self.process_name,
            entry_name,
            classname=classname,
            token=entry_name,
            trigger_frequency='every {0}'.format(SECONDS_IN_CENTURY),
            is_on=False,
            description='Runtime freerun object to facilitate CUSTOM RUN MODES for workflow',
        )

    @property
    def flow_id(self):
        flow_entry = self.flow_dao.get_one([self.flow_name, self.timeperiod])
        return flow_entry.db_id

    @property
    def step_id(self):
        step_entry = self.step_dao.get_one([self.flow_name, self.step_name, self.timeperiod])
        return step_entry.db_id

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

    @valid_action_request
    def action_recover(self):
        """
        - make sure that the job is either finished or in progress
          i.e. the job is in [STATE_IN_PROGRESS, STATE_NOOP, STATE_PROCESSED, STATE_SKIPPED]
        - TBD: set a special flag, understood by governing State Machine and GC that the
          related_uow is either in [STATE_PROCESSED, STATE_INVALID, STATE_CANCELED]
        - invalidate the UOW and trigger the GC
        :return RESPONSE_OK if the UOW was submitted and RESPONSE_NOT_OK otherwise
        """
        pass

    @valid_action_request
    def action_run_one_step(self):
        """
        - make sure that the job is finished
          i.e. the job is in [STATE_NOOP, STATE_PROCESSED, STATE_SKIPPED]
        - submit a FREERUN UOW for given (process_name::flow_name::step_name, timeperiod)
        :return RESPONSE_OK if the UOW was submitted and RESPONSE_NOT_OK otherwise
        """
        if not self.job_record or not self.job_record.is_finished:
            return RESPONSE_NOT_OK

        flow_request = FlowRequest(self.process_name, self.flow_name, self.step_name,
                                   RUN_MODE_RUN_ONE,
                                   self.timeperiod, self.start_timeperiod, self.end_timeperiod)

        state_machine = self.scheduler.timetable.state_machines[STATE_MACHINE_FREERUN]
        state_machine.manage_schedulable(self.freerun_process_entry, flow_request)
        return RESPONSE_OK

    @valid_action_request
    def action_run_from_step(self):
        """
        - make sure that the job is finished
          i.e. the job is in [STATE_NOOP, STATE_PROCESSED, STATE_SKIPPED]
        - submit a FREERUN UOW for given (process_name::flow_name::step_name, timeperiod)
        :return RESPONSE_OK if the UOW was submitted and RESPONSE_NOT_OK otherwise
        """
        if not self.job_record or not self.job_record.is_finished:
            return RESPONSE_NOT_OK

        flow_request = FlowRequest(self.process_name, self.flow_name, self.step_name,
                                   RUN_MODE_RUN_FROM,
                                   self.timeperiod, self.start_timeperiod, self.end_timeperiod)

        state_machine = self.scheduler.timetable.state_machines[STATE_MACHINE_FREERUN]
        state_machine.manage_schedulable(self.freerun_process_entry, flow_request)
        return RESPONSE_OK

    @valid_action_request
    @safe_json_response
    def action_get_step_log(self):
        try:
            resp = self.log_recording_dao.get_one(self.step_id).document
        except (TypeError, LookupError):
            resp = {'response': 'no related step log'}
        return resp

    @valid_action_request
    @safe_json_response
    def action_get_flow_log(self):
        try:
            resp = self.log_recording_dao.get_one(self.flow_id).document
        except (TypeError, LookupError):
            resp = {'response': 'no related workflow log'}
        return resp
