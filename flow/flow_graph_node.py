__author__ = 'Bohdan Mushkevych'

from datetime import datetime

from db.model.step import Step, STATE_REQUESTED, STATE_INVALID, STATE_IN_PROGRESS, STATE_PROCESSED
from db.dao.step_dao import StepDao
from flow.execution_context import ContextDriven


class FlowGraphNode(ContextDriven):
    def __init__(self, name, dependent_on_names, step_instantiable):
        super(FlowGraphNode, self).__init__(name)

        self.name = name
        self.dependent_on_names = dependent_on_names
        self.step_instantiable = step_instantiable
        self.step_dao = None
        self.step = None

    def set_context(self, context):
        super(FlowGraphNode, self).set_context(context)
        self.step_dao = StepDao(self.logger)

    def mark_start(self):
        """ performs step start-up, such as db and context updates """
        self.step = Step()
        self.step.created_at = datetime.utcnow()
        self.step.started_at = datetime.utcnow()
        self.step.flow_name = self.context.flow.flow_name
        self.step.timeperiod = self.context.timeperiod
        self.step.related_flow = self.context.flow_id
        self.step.state = STATE_REQUESTED
        self.step_dao.update(self.step)

    def mark_failure(self):
        """ perform step post-failure activities, such as db update """
        self.step.finished_at = datetime.utcnow()
        self.step.state = STATE_INVALID
        self.step_dao.update(self.step)

    def mark_success(self):
        """ perform activities in case of the step successful completion """
        self.step.finished_at = datetime.utcnow()
        self.step.state = STATE_PROCESSED
        self.step_dao.update(self.step)

    def run(self, context, execution_cluster):
        self.set_context(context)
        self.mark_start()

        step_instance = self.step_instantiable.instantiate()
        step_instance.do_pre(context, execution_cluster)
        if not step_instance.is_pre_completed:
            self.mark_failure()
            return False

        step_instance.do_main(context, execution_cluster)
        if not step_instance.is_pre_completed:
            self.mark_failure()
            return False

        step_instance.do_post(context, execution_cluster)
        if not step_instance.is_complete:
            self.mark_failure()
            return False

        self.mark_success()
        return step_instance.is_complete
