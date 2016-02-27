__author__ = 'Bohdan Mushkevych'

from flow.execution_context import ContextDriven


class AbstractAction(ContextDriven):
    def __init__(self, name, kwargs=None):
        super(AbstractAction, self).__init__(name)
        self.name = name
        self.kwargs = {} if not kwargs else kwargs

    def __del__(self):
        self.cleanup()
        if self.logger:
            self.logger.info('Action {0} finished.'.format(self.name))

    def do(self, context, execution_cluster):
        raise NotImplementedError('method do must be implemented by {0}'.format(self.__class__.__name__))

    def cleanup(self):
        pass
