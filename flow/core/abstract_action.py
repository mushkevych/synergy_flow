__author__ = 'Bohdan Mushkevych'

from flow.core.execution_context import get_action_logger


class AbstractAction(object):
    """ abstraction for action: API sequence is to *do* and *cleanup*
        NOTICE:  instances of this class must be context-agnostic and stateless
                 i.e. the same instance of an action can be used in multiple flows or steps  """

    def __init__(self, name, log_tag=None, **kwargs):
        self.name = name
        self.log_tag = log_tag
        self.kwargs = {} if not kwargs else kwargs

    def __del__(self):
        self.cleanup()
        if self.logger:
            self.logger.info('Action {0} finished.'.format(self.name))

    def get_logger(self, flow_name, step_name, context):
        return get_action_logger(flow_name, step_name, self.name, context)

    def do(self, context, execution_cluster):
        raise NotImplementedError('method do must be implemented by {0}'.format(self.__class__.__name__))

    def cleanup(self):
        pass
