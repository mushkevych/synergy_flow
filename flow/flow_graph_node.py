__author__ = 'Bohdan Mushkevych'

from datetime import datetime

from db.model.step import Step, STATE_REQUESTED, STATE_INVALID, STATE_IN_PROGRESS, STATE_PROCESSED
from db.dao.step_dao import StepDao
from flow.execution_context import ContextDriven


class FlowGraphNode(ContextDriven):
    def __init__(self, name, dependent_on_names, step_instance):
        super(FlowGraphNode, self).__init__(name)

        self.name = name
        self.dependent_on_names = dependent_on_names
        self.step_instance = step_instance
        self.step_dao = None
        self.step_model = None

        # attributes _prev and _next contains FlowGraphNodes that preceeds and follows this node
        # these are managed by the Flow.append
        self._prev = list()
        self._next = list()

    def set_context(self, context):
        super(FlowGraphNode, self).set_context(context)
        self.step_dao = StepDao(self.logger)

    def mark_start(self):
        """ performs step start-up, such as db and context updates """
        self.step_model = Step()
        self.step_model.created_at = datetime.utcnow()
        self.step_model.started_at = datetime.utcnow()
        self.step_model.flow_name = self.context.flow_model.flow_name
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

    def run(self, context, execution_cluster):
        self.set_context(context)
        self.mark_start()

        self.step_instance.do_pre(context, execution_cluster)
        if not self.step_instance.is_pre_completed:
            self.mark_failure()
            return False

        self.step_instance.do_main(context, execution_cluster)
        if not self.step_instance.is_pre_completed:
            self.mark_failure()
            return False

        self.step_instance.do_post(context, execution_cluster)
        if not self.step_instance.is_complete:
            self.mark_failure()
            return False

        self.mark_success()
        return self.step_instance.is_complete
