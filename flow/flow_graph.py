__author__ = 'Bohdan Mushkevych'

from flow.flow_graph_node import FlowGraphNode


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

    def get_next_node(self):
        """ FIXME: rewrite """
        return FlowGraphNode(None, None, None)
