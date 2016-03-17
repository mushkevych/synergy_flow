__author__ = 'Bohdan Mushkevych'

from flow.core.abstract_cluster import AbstractCluster


class EphemeralCluster(AbstractCluster):
    """ implementation of the abstract API for the local, non-distributed environment """
    def __init__(self, name, context, **kwargs):
        super(EphemeralCluster, self).__init__(name, context, kwargs=kwargs)

    def run_pig_step(self, uri_script, **kwargs):
        pass

    def run_spark_step(self, uri_script, **kwargs):
        pass

    def run_hadoop_step(self, uri_script, **kwargs):
        pass

    def run_shell_command(self, uri_script, **kwargs):
        pass
