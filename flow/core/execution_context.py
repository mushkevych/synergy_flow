__author__ = 'Bohdan Mushkevych'

import os
from synergy.system.data_logging import Logger


def get_logger(log_tag, context):
    log_file = os.path.join(context.settings['log_directory'], '{0}.log'.format(log_tag))
    append_to_console = context.settings['under_test'],
    redirect_stdstream = not context.settings['under_test']
    return Logger(log_file, log_tag, append_to_console, redirect_stdstream)


class ExecutionContext(object):
    """ set of attributes that identify Flow execution:
        - timeperiod boundaries of the run
        - environment-specific settings, where the flow is run
    """
    def __init__(self, start_timeperiod, end_timeperiod, settings, number_of_clusters=2, flow_graph=None, flow_model=None):
        assert isinstance(settings, dict)

        self.timeperiod = start_timeperiod
        self.settings = settings
        self.number_of_clusters = number_of_clusters
        self._flow_graph = flow_graph
        self._flow_model = flow_model

    @property
    def flow_graph(self):
        return self._flow_graph

    @flow_graph.setter
    def flow_graph(self, value):
        self._flow_graph = value

    @property
    def flow_model(self):
        return self._flow_model

    @flow_model.setter
    def flow_model(self, value):
        self._flow_model = value

    @property
    def flow_id(self):
        return self._flow_model.db_id


class ContextDriven(object):
    """ common ancestor for all types that require *context*,
        and perform same set of initialization of it """
    def __init__(self, log_tag=None):
        if log_tag is None:
            log_tag = self.__class__.__name__

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
        self.logger = get_logger(self.log_tag, context)
