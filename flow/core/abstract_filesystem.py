__author__ = 'Bohdan Mushkevych'

from flow.core.execution_context import ExecutionContext


class AbstractFilesystem(object):
    """ abstraction for filesystem """
    def __init__(self, logger, context, **kwargs):
        assert isinstance(context, ExecutionContext)
        self.context = context
        self.logger = logger
        self.kwargs = {} if not kwargs else kwargs

    def mkdir(self, uri_path, **kwargs):
        pass

    def rmdir(self, uri_path, **kwargs):
        pass

    def rm(self, uri_path, **kwargs):
        pass

    def cp(self, uri_source, uri_target, **kwargs):
        pass

    def mv(self, uri_source, uri_target, **kwargs):
        pass

    def copyToLocal(self, uri_source, uri_target, **kwargs):
        pass

    def copyFromLocal(self, uri_source, uri_target, **kwargs):
        pass
