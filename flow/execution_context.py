__author__ = 'Bohdan Mushkevych'

import os
from Queue import Queue
from synergy.system.data_logging import Logger


class ExecutionContext(object):
    def __init__(self, timeperiod, settings, number_of_clusters=2, flow_graph=None, flow=None):
        assert isinstance(settings, dict)

        self.timeperiod = timeperiod
        self.settings = settings
        self.number_of_clusters = number_of_clusters
        self._flow_graph = flow_graph
        self._flow = flow

        # multi-threading queue
        self.cluster_queue = Queue()

    @property
    def flow_graph(self):
        return self._flow_graph

    @flow_graph.setter
    def flow_graph(self, value):
        self._flow_graph = value

    @property
    def flow(self):
        return self._flow

    @flow.setter
    def flow(self, value):
        self._flow = value

    @property
    def flow_id(self):
        return self._flow.db_id


class ContextDriven(object):
    def __init__(self, log_tag):
        self.log_tag = log_tag
        self.context = None
        self.timeperiod = None
        self.settings = None
        self.logger = None

    def set_context(self, context):
        assert isinstance(context, ExecutionContext)

        self.context = context
        self.timeperiod = context.timeperiod
        self.settings = context.settings

        log_file = os.path.join(context.settings['log_directory'], '{0}.log'.format(self.__class__.__name__))
        append_to_console = context.settings['under_test'],
        redirect_stdstream = not context.settings['under_test']
        self.logger = Logger(log_file, self.log_tag, append_to_console, redirect_stdstream)
