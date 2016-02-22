__author__ = 'Bohdan Mushkevych'


class AbstractAction(object):
    def __init__(self, name, kwargs=None):
        self.name = name
        self.kwargs = {} if not kwargs else kwargs
        self.logger = None

    def __del__(self):
        self.cleanup()
        if self.logger:
            self.logger.info('Action {0} finished.'.format(self.name))

    def set_context(self, context):
        pass

    def do(self, context):
        raise NotImplementedError('method do must be implemented by {0}'.format(self.__class__.__name__))

    def cleanup(self):
        raise NotImplementedError('method cleanup must be implemented by {0}'.format(self.__class__.__name__))
