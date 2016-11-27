__author__ = 'Bohdan Mushkevych'

import time
from flow.core.abstract_action import AbstractAction


class SleepAction(AbstractAction):
    def __init__(self, seconds):
        super(SleepAction, self).__init__('Sleep Action')
        self.seconds = seconds

    def run(self, execution_cluster):
        time.sleep(self.seconds)


class ShellCommandAction(AbstractAction):
    def __init__(self, shell_command):
        super(ShellCommandAction, self).__init__('Shell Command Action')
        self.shell_command = shell_command

    def run(self, execution_cluster):
        execution_cluster.run_shell_command(self.shell_command)


class IdentityAction(AbstractAction):
    """ this class is intended to be used by Unit Tests """
    def __init__(self):
        super(IdentityAction, self).__init__('Identity Action')

    def run(self, execution_cluster):
        self.logger.info('identity action: *do* completed')


class FailureAction(AbstractAction):
    """ this class is intended to be used by Unit Tests """
    def __init__(self):
        super(FailureAction, self).__init__('Failure Action')

    def run(self, execution_cluster):
        raise UserWarning('failure action: raising exception')


class PigAction(AbstractAction):
    """ executes a pig script on the given cluster """
    def __init__(self, uri_script, **kwargs):
        super(PigAction, self).__init__('Pig Action', kwargs)
        self.uri_script = uri_script

    def run(self, execution_cluster):
        is_successful = execution_cluster.run_pig_step(
            uri_script=self.uri_script,
            start_timeperiod=self.start_timeperiod,
            end_timeperiod=self.end_timeperiod,
            timeperiod=self.timeperiod,
            **self.kwargs)
        if not is_successful:
            raise UserWarning('Pig Action failed on {0}'.format(self.uri_script))


class SparkAction(AbstractAction):
    """ executes a spark script on the given cluster """
    def __init__(self, uri_script, language, **kwargs):
        super(SparkAction, self).__init__('Spark Action', kwargs)
        self.uri_script = uri_script
        self.language = language

    def run(self, execution_cluster):
        is_successful = execution_cluster.run_spark_step(
            uri_script=self.uri_script,
            language=self.language,
            **self.kwargs)
        if not is_successful:
            raise UserWarning('Spark Action failed on {0}'.format(self.uri_script))
