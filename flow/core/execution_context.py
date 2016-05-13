__author__ = 'Bohdan Mushkevych'

import os
from synergy.system.system_logger import Logger


LOGS = dict()


def get_flow_logger(flow_name, settings):
    if flow_name in LOGS:
        return LOGS[flow_name].get_logger()

    # make sure the path exist
    log_folder = os.path.join(settings['log_directory'], flow_name)
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_file = os.path.join(settings['log_directory'], flow_name, '{0}.log'.format(flow_name))
    append_to_console = settings['under_test'],
    redirect_stdstream = not settings['under_test']
    LOGS[flow_name] = Logger(log_file, flow_name, append_to_console, redirect_stdstream)
    return LOGS[flow_name].get_logger()


def get_cluster_logger(flow_name, cluster_name, settings):
    logger = get_flow_logger(flow_name, settings)
    return logger.getChild(cluster_name)


def get_step_logger(flow_name, step_name, settings):
    fqlt = '{0}.{1}'.format(flow_name, step_name)
    if fqlt in LOGS:
        return LOGS[fqlt].get_logger()

    log_file = os.path.join(settings['log_directory'], flow_name, '{0}.log'.format(step_name))
    append_to_console = settings['under_test'],
    redirect_stdstream = not settings['under_test']
    LOGS[fqlt] = Logger(log_file, step_name, append_to_console, redirect_stdstream)
    return LOGS[fqlt].get_logger()


def get_action_logger(flow_name, step_name, action_name, settings):
    logger = get_step_logger(flow_name, step_name, settings)
    return logger.getChild(action_name)


class ExecutionContext(object):
    """ set of attributes that identify Flow execution:
        - timeperiod boundaries of the run
        - environment-specific settings, where the flow is run
    """
    def __init__(self, flow_name, timeperiod, settings, number_of_clusters=2, flow_graph=None, flow_model=None):
        assert isinstance(settings, dict)

        self.flow_name = flow_name
        self.timeperiod = timeperiod
        self.settings = settings
        self.number_of_clusters = number_of_clusters
        self.flow_graph = flow_graph
        self.flow_model = flow_model

    @property
    def flow_id(self):
        return self.flow_model.db_id


class ContextDriven(object):
    """ common ancestor for all types that require *context*,
        and perform same set of initialization of it """
    def __init__(self):
        self.context = None
        self.flow_name = None
        self.timeperiod = None
        self.settings = None
        self.logger = None
        self.is_context_set = False

    def set_context(self, context, **kwargs):
        assert isinstance(context, ExecutionContext)
        self.context = context
        self.flow_name = context.flow_name
        self.timeperiod = context.timeperiod
        self.settings = context.settings
        self.logger = self.get_logger()
        self.is_context_set = True

    def get_logger(self):
        raise NotImplementedError('method get_logger must be implemented by {0}'.format(self.__class__.__name__))
