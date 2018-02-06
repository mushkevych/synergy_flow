__author__ = 'Bohdan Mushkevych'

from google.cloud import dataproc

from synergy.conf import settings
from flow.core.abstract_cluster import AbstractCluster
from flow.core.gcp_filesystem import GcpFilesystem


def read_file_content(file_uri):
    with open(file_uri, mode='r') as py_file:
        file_content = py_file.read()
    return file_content


class GcpCluster(AbstractCluster):
    """ implementation of the Google Cloud Platform Dataproc API """

    def __init__(self, name, context, **kwargs):
        super(GcpCluster, self).__init__(name, context, kwargs=kwargs)
        self._filesystem = GcpFilesystem(self.logger, context, **kwargs)

    @property
    def filesystem(self):
        return self._filesystem

    def run_pig_step(self, uri_script, **kwargs):
        program_body = read_file_content(uri_script)
        spark_cmd = PigCommand.run(script=program_body, **kwargs)

        self.logger.info('command id: {0}; Status: {1}'.format(spark_cmd.id, spark_cmd.status))
        self.logger.info('command result: {0}'.format(spark_cmd.get_results()))
        self.logger.info('command log: {0}'.format(spark_cmd.get_log()))

    def run_spark_step(self, uri_script, language, **kwargs):
        program_body = read_file_content(uri_script)
        spark_cmd = SparkCommand.run(program=program_body, language=language, **kwargs)

        self.logger.info('command id: {0}; Status: {1}'.format(spark_cmd.id, spark_cmd.status))
        self.logger.info('command result: {0}'.format(spark_cmd.get_results()))
        self.logger.info('command log: {0}'.format(spark_cmd.get_log()))

    def run_hadoop_step(self, uri_script, **kwargs):
        raise NotImplementedError('method run_hadoop_step is not yet supported for the Qubole cluster')

    def run_shell_command(self, uri_script, **kwargs):
        program_body = read_file_content(uri_script)
        spark_cmd = ShellCommand.run(script=program_body, **kwargs)

        self.logger.info('command id: {0}; Status: {1}'.format(spark_cmd.id, spark_cmd.status))
        self.logger.info('command result: {0}'.format(spark_cmd.get_results()))
        self.logger.info('command log: {0}'.format(spark_cmd.get_log()))
