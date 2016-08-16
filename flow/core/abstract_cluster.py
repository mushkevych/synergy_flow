__author__ = 'Bohdan Mushkevych'

from flow.core.execution_context import ExecutionContext, get_cluster_logger
from flow.core.abstract_filesystem import AbstractFilesystem


class ClusterError(Exception):
    pass


class AbstractCluster(object):
    """ abstraction for action execution environment
        API sequence is to launch the cluster, perform one or more steps/commands and terminate """
    def __init__(self, name, context, filesystem, **kwargs):
        assert isinstance(context, ExecutionContext)
        assert isinstance(filesystem, AbstractFilesystem)

        self.name = name
        self.context = context
        self._filesystem = filesystem
        self.logger = get_cluster_logger(context.flow_name, self.name, context.settings)
        self.kwargs = {} if not kwargs else kwargs

    @property
    def filesystem(self):
        return self._filesystem

    def run_pig_step(self, uri_script, **kwargs):
        pass

    def run_spark_step(self, uri_script, language, **kwargs):
        pass

    def run_hadoop_step(self, uri_script, **kwargs):
        pass

    def run_shell_command(self, uri_script, **kwargs):
        pass

    def launch(self):
        pass

    def terminate(self):
        pass
