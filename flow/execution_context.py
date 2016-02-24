__author__ = 'Bohdan Mushkevych'

from Queue import Queue


class ExecutionContext(object):
    def __init__(self, timeperiod, settings, number_of_clusters=2, flow_graph=None, flow_id=None):
        assert isinstance(settings, dict)

        self.timeperiod = timeperiod
        self.settings = settings
        self.number_of_clusters = number_of_clusters
        self._flow_graph = flow_graph
        self._flow_id = flow_id

        # multi-threading queue
        self.cluster_queue = Queue()

    @property
    def flow_graph(self):
        return self._flow_graph

    @flow_graph.setter
    def flow_graph(self, value):
        self._flow_graph = value

    @property
    def flow_id(self):
        return self._flow_id

    @flow_id.setter
    def flow_id(self, value):
        self._flow_id = value
