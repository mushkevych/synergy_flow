__author__ = 'Bohdan Mushkevych'

from datetime import datetime

from flow.core.execution_context import ContextDriven, get_step_logger, valid_context
from synergy.system.log_recording_handler import LogRecordingHandler

from flow.db.model.step import Step, STATE_EMBRYO, STATE_INVALID, STATE_PROCESSED, STATE_IN_PROGRESS
from flow.db.dao.step_dao import StepDao


class FlowGraphNode(ContextDriven):
    """ represents a Node in the FlowGraph """
    def __init__(self, step_name, step_executor):
        super(FlowGraphNode, self).__init__()

        self.step_name = step_name
        self.step_executor = step_executor
        self.step_dao = None
        self.step_entry = None
        self.log_recording_handler = None

        # attributes _prev and _next contains FlowGraphNodes that precedes and follows this node
        # these are managed by the FlowGraph.append
        self._prev = list()
        self._next = list()

    def set_context(self, context,  **kwargs):
        super(FlowGraphNode, self).set_context(context, **kwargs)
        self.step_executor.set_context(context)
        self.step_dao = StepDao(self.logger)

        if not self.step_entry:
            # Normal flow
            self.step_entry = Step()
            self.step_entry.created_at = datetime.utcnow()
            self.step_entry.flow_name = self.context.flow_name
            self.step_entry.timeperiod = self.context.timeperiod
            self.step_entry.related_flow = self.context.flow_id
            self.step_entry.state = STATE_EMBRYO
        else:
            # ExecutionEngine is performing recovery
            # step_entry has been loaded from the DB
            pass

    def get_logger(self):
        return get_step_logger(self.flow_name, self.step_name, self.settings)

    def mark_start(self):
        """ performs step start-up, such as db and context updates """
        self.step_entry.started_at = datetime.utcnow()
        self.step_entry.state = STATE_IN_PROGRESS
        self.step_dao.update(self.step_entry)

        # enable log recording into DB
        self.log_recording_handler = LogRecordingHandler(self.get_logger(), self.step_entry.db_id)
        self.log_recording_handler.attach()

    def _mark_finish(self, state):
        self.step_entry.finished_at = datetime.utcnow()
        self.step_entry.state = state
        self.step_dao.update(self.step_entry)

        if self.log_recording_handler:
            self.log_recording_handler.detach()

    def mark_failure(self):
        """ perform step post-failure activities, such as db update """
        self._mark_finish(STATE_INVALID)

    def mark_success(self):
        """ perform activities in case of the step successful completion """
        self._mark_finish(STATE_PROCESSED)

    @valid_context
    def run(self, execution_cluster):
        self.mark_start()

        self.step_executor.do(execution_cluster)
        if self.step_executor.is_complete:
            self.mark_success()
        else:
            self.mark_failure()
        return self.step_executor.is_complete
