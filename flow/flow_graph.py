__author__ = 'Bohdan Mushkevych'

from datetime import datetime

from db.dao.step_dao import StepDao
from db.dao.flow_dao import FlowDao
from db.model.flow import Flow, STATE_REQUESTED, STATE_INVALID, STATE_PROCESSED
from flow.flow_graph_node import FlowGraphNode
from flow.execution_context import ContextDriven


class FlowGraph(ContextDriven):
    def __init__(self, flow_name):
        super(FlowGraph, self).__init__(flow_name)
        self.flow_name = flow_name
        self._dict = dict()
        self.flow_dao = None

    def __getitem__(self, key):
        return self._dict[key]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def __eq__(self, other):
        return self._dict == other._dict

    def __contains__(self, item):
        return item in self._dict

    def append(self, name, step_klass, dependent_on_names):
        node = FlowGraphNode(name, step_klass, dependent_on_names)
        self._dict[name] = node

    def is_step_blocked(self, step_name):
        for preceding_step_name in self[step_name].dependent_on_steps:
            preceding_node = self[preceding_step_name]
            if preceding_node.step_instance and preceding_node.step_instance.is_complete:
                return True
        return False

    def set_context(self, context):
        super(FlowGraph, self).set_context(context)
        self.flow_dao = FlowDao(self.logger)

    # FIXME: rewrite
    def get_next_node(self):
        return FlowGraphNode(None, None, None)

    def mark_start(self, context):
        """ performs flow start-up, such as db and context updates """
        self.set_context(context)

        flow = Flow()
        flow.flow_name = self.flow_name
        flow.timeperiod = context.timeperiod
        flow.created_at = datetime.utcnow()
        flow.started_at = datetime.utcnow()
        flow.state = STATE_REQUESTED

        step_dao = StepDao(self.logger)
        try:
            # remove, if exists, existing Flow and related Steps
            db_key = [flow.flow_name, flow.timeperiod]
            existing_flow = self.flow_dao.get_one(db_key)
            step_dao.remove_by_flow_id(existing_flow.db_id)
            self.flow_dao.remove(db_key)
        except LookupError:
            # no flow record for given key was present in the database
            pass
        finally:
            self.flow_dao.update(flow)
            context.flow = flow

    def mark_failure(self, context):
        """ perform flow post-failure activities, such as db update """
        context.flow.finished_at = datetime.utcnow()
        context.flow.state = STATE_INVALID
        self.flow_dao.update(context.flow)

    def mark_success(self, context):
        """ perform activities in case of the flow successful completion """
        context.flow.finished_at = datetime.utcnow()
        context.flow.state = STATE_PROCESSED
        self.flow_dao.update(context.flow)
