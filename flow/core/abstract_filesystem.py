import os

__author__ = 'Bohdan Mushkevych'

from flow.core.execution_context import ExecutionContext


def splitpath(uri_path):
    head, tail = os.path.split(uri_path)
    return splitpath(head) + [tail] if head and head != uri_path else [head or tail]


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

    def exists(self, uri_path, **kwargs):
        pass
