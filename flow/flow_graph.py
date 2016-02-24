__author__ = 'Bohdan Mushkevych'

from datetime import datetime

from flow.flow_graph_node import FlowGraphNode
from db.model.flow import Flow, STATE_REQUESTED


class FlowGraph(object):
    def __init__(self, flow_name):
        self.flow_name = flow_name
        self._dict = dict()

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

    @property
    def is_step_blocked(self, step_name):
        for preceding_step_name in self[step_name].dependent_on_steps:
            preceding_node = self[preceding_step_name]
            if preceding_node.step_instance and preceding_node.step_instance.is_complete:
                return True
        return False

    # FIXME: rewrite
    def get_next_node(self):
        return FlowGraphNode(None, None, None)

    # FIXME: rewrite
    def start(self, context):
        """ performs flow start-up, such as db and context updates """

        flow = Flow()
        flow.created_at = datetime.utcnow()
        flow.started_at = datetime.utcnow()
        flow.state = STATE_REQUESTED

        try:
            db_key = [self.flow_graph.flow_name, context.timeperiod]
            self.flow_dao.get_one(db_key)
            self.flow_dao.remove(db_key)
        except LookupError:
            # no flow record for given key was present in the database
            pass
        finally:
            db_id = self.flow_dao.update(flow)
            context.flow_id = db_id

    def failed(self, context):
        """ perform activities in case of the flow failure """
        pass

    def succeed(self, context):
        """ perform activities in case of the flow successful completion """
        pass
