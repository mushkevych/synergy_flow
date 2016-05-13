__author__ = 'Bohdan Mushkevych'

import time

from flow.core.abstract_action import AbstractAction


class SleepAction(AbstractAction):
    def __init__(self, seconds):
        super(SleepAction, self).__init__('Sleep Action')
        self.seconds = seconds

    def do(self, execution_cluster):
        time.sleep(self.seconds)


class ShellCommandAction(AbstractAction):
    def __init__(self, shell_command):
        super(ShellCommandAction, self).__init__('Shell Command Action')
        self.shell_command = shell_command

    def do(self, execution_cluster):
        execution_cluster.run_shell_command(self.shell_command)


class IdentityAction(AbstractAction):
    """ this class is intended to be used by Unit Tests """
    def __init__(self):
        super(IdentityAction, self).__init__('Identity Action')

    def do(self, execution_cluster):
        self.logger.info('identity action: *do* completed')


class FailureAction(AbstractAction):
    """ this class is intended to be used by Unit Tests """
    def __init__(self):
        super(FailureAction, self).__init__('Failure Action')

    def do(self, execution_cluster):
        raise UserWarning('failure action: raising exception')
