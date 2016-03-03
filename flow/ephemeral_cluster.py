__author__ = 'Bohdan Mushkevych'

from flow.abstract_cluster import AbstractCluster


class EphemeralCluster(AbstractCluster):
    def __init__(self, name, context, **kwargs):
        super(EphemeralCluster, self).__init__(name, context, kwargs)

    def run_pig_step(self, uri_script, **kwargs):
        pass

    def run_spark_step(self, uri_script, **kwargs):
        pass

    def run_hadoop_step(self, uri_script, **kwargs):
        pass

    def run_shell_command(self, uri_script, **kwargs):
        pass
