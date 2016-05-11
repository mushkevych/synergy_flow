__author__ = 'Bohdan Mushkevych'

try:
    # python 2.x
    import subprocess32 as subprocess
except ImportError:
    # python 3.3+
    import subprocess

from flow.core.abstract_cluster import AbstractCluster


class EphemeralCluster(AbstractCluster):
    """ implementation of the abstract API for the local, non-distributed environment """

    def __init__(self, name, context, **kwargs):
        super(EphemeralCluster, self).__init__(name, context, kwargs=kwargs)

    def run_pig_step(self, uri_script, **kwargs):
        step_args = []
        for k, v in kwargs.items():
            step_args.append('-p')
            step_args.append('{0}={1}'.format(k, v))
        return self.run_shell_command('pig -f {0} {1}'.format(uri_script, ' '.join(step_args)))

    def run_spark_step(self, uri_script, **kwargs):
        pass

    def run_hadoop_step(self, uri_script, **kwargs):
        step_args = []
        for k, v in kwargs.items():
            step_args.append('-D')
            step_args.append('{0}={1}'.format(k, v))
        return self.run_shell_command('hadoop jar {0} {1}'.format(uri_script, ' '.join(step_args)))

    def run_shell_command(self, uri_script, **kwargs):
        step_args = []
        for k, v in kwargs.items():
            step_args.append('{0} {1}'.format(k, v))

        return subprocess.check_output('{0} {1}'.format(uri_script, ' '.join(step_args)),
                                       stderr=subprocess.STDOUT,
                                       shell=True)
