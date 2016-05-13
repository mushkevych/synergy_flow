__author__ = 'Bohdan Mushkevych'

import os
from synergy.system.system_logger import Logger


LOGS = dict()


def get_flow_logger(flow_name, context):
    if flow_name in LOGS:
        return LOGS[flow_name].get_logger()

    log_file = os.path.join(context.settings['log_directory'], flow_name, '{0}.log'.format(flow_name))
    append_to_console = context.settings['under_test'],
    redirect_stdstream = not context.settings['under_test']
    LOGS[flow_name] = Logger(log_file, flow_name, append_to_console, redirect_stdstream)
    return LOGS[flow_name].get_logger()


def get_step_logger(flow_name, step_name, context):
    fqlt = '{0}.{1}'.format(flow_name, step_name)
    if fqlt in LOGS:
        return LOGS[fqlt].get_logger()

    log_file = os.path.join(context.settings['log_directory'], flow_name, '{0}.log'.format(step_name))
    append_to_console = context.settings['under_test'],
    redirect_stdstream = not context.settings['under_test']
    LOGS[fqlt] = Logger(log_file, step_name, append_to_console, redirect_stdstream)
    return LOGS[fqlt].get_logger()


def get_action_logger(flow_name, step_name, action_name, context):
    logger = get_step_logger(flow_name, step_name, context)
    return logger.get_logger().getChild(action_name)


class ExecutionContext(object):
    """ set of attributes that identify Flow execution:
        - timeperiod boundaries of the run
        - environment-specific settings, where the flow is run
    """
    def __init__(self, timeperiod, settings, number_of_clusters=2, flow_graph=None, flow_model=None):
        assert isinstance(settings, dict)

        self.timeperiod = timeperiod
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
        self.is_context_set = False

    def set_context(self, context):
        assert isinstance(context, ExecutionContext)
        self.context = context
        self.timeperiod = context.timeperiod
        self.settings = context.settings
        self.is_context_set = True
