__author__ = 'Bohdan Mushkevych'

from flow.core.execution_context import ExecutionContext, get_cluster_logger


class AbstractFilesystem(object):
    """ abstraction for filesystem """
    def __init__(self, cluster_name, context, **kwargs):
        assert isinstance(context, ExecutionContext)

        self.cluster_name = cluster_name
        self.context = context
        self.logger = get_cluster_logger(context.flow_name, self.cluster_name, context.settings)
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
