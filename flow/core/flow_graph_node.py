__author__ = 'Bohdan Mushkevych'

from datetime import datetime

from flow.core.execution_context import ContextDriven, get_step_logger

from flow.db.model.step import Step, STATE_REQUESTED, STATE_INVALID, STATE_PROCESSED
from flow.db.dao.step_dao import StepDao


class FlowGraphNode(ContextDriven):
    """ represents a Node in the FlowGraph """
    def __init__(self, step_name, dependent_on_names, step_executor):
        super(FlowGraphNode, self).__init__()

        self.step_name = step_name
        self.dependent_on_names = dependent_on_names
        self.step_executor = step_executor
        self.step_dao = None
        self.step_model = None

        # attributes _prev and _next contains FlowGraphNodes that precedes and follows this node
        # these are managed by the FlowGraph.append
        self._prev = list()
        self._next = list()

    def set_context(self, context,  **kwargs):
        super(FlowGraphNode, self).set_context(context, **kwargs)
        self.step_executor.set_context(context)
        self.step_dao = StepDao(self.logger)

    def get_logger(self):
        return get_step_logger(self.flow_name, self.step_name, self.settings)

    def mark_start(self):
        """ performs step start-up, such as db and context updates """
        self.step_model = Step()
        self.step_model.created_at = datetime.utcnow()
        self.step_model.started_at = datetime.utcnow()
        self.step_model.flow_name = self.context.flow_name
        self.step_model.timeperiod = self.context.timeperiod
        self.step_model.related_flow = self.context.flow_id
        self.step_model.state = STATE_REQUESTED
        self.step_dao.update(self.step_model)

    def mark_failure(self):
        """ perform step post-failure activities, such as db update """
        self.step_model.finished_at = datetime.utcnow()
        self.step_model.state = STATE_INVALID
        self.step_dao.update(self.step_model)

    def mark_success(self):
        """ perform activities in case of the step successful completion """
        self.step_model.finished_at = datetime.utcnow()
        self.step_model.state = STATE_PROCESSED
        self.step_dao.update(self.step_model)

    def run(self, execution_cluster):
        assert self.is_context_set is True
        self.mark_start()

        self.step_executor.do_pre(execution_cluster)
        if not self.step_executor.is_pre_completed:
            self.mark_failure()
            return False

        self.step_executor.do_main(execution_cluster)
        if not self.step_executor.is_pre_completed:
            self.mark_failure()
            return False

        self.step_executor.do_post(execution_cluster)
        if not self.step_executor.is_complete:
            self.mark_failure()
            return False

        self.mark_success()
        return self.step_executor.is_complete
