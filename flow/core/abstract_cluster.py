__author__ = 'Bohdan Mushkevych'

from flow.core.execution_context import ExecutionContext, get_cluster_logger


class ClusterError(Exception):
    pass


class AbstractCluster(object):
    """ abstraction for action execution environment
        API sequence is to launch the cluster, perform one or more steps/commands and terminate """
    def __init__(self, name, context, **kwargs):
        assert isinstance(context, ExecutionContext)

        self.name = name
        self.context = context
        self.logger = get_cluster_logger(context.flow_name, self.name, context.settings)
        self.kwargs = {} if not kwargs else kwargs

    def run_pig_step(self, uri_script, **kwargs):
        pass

    def run_spark_step(self, uri_script, **kwargs):
        pass

    def run_hadoop_step(self, uri_script, **kwargs):
        pass

    def run_shell_command(self, uri_script, **kwargs):
        pass

    def launch(self):
        pass

    def terminate(self):
        pass
