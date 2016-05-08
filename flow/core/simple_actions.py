__author__ = 'Bohdan Mushkevych'

import time

from flow.core.abstract_action import AbstractAction


class SleepAction(AbstractAction):
    def __init__(self, seconds, **kwargs):
        super(SleepAction, self).__init__('Sleep Action', kwargs)
        self.seconds = seconds

    def do(self, context, execution_cluster):
        self.set_context(context)
        time.sleep(self.seconds)


class ShellCommandAction(AbstractAction):
    def __init__(self, shell_command, **kwargs):
        super(ShellCommandAction, self).__init__('Shell Command Action', kwargs)
        self.shell_command = shell_command

    def do(self, context, execution_cluster):
        self.set_context(context)
        execution_cluster.run_shell_command(self.shell_command)


class IdentityAction(AbstractAction):
    """ this class is intended to be used by Unit Tests """
    def __init__(self, **kwargs):
        super(IdentityAction, self).__init__('Identity Action', kwargs)

    def do(self, context, execution_cluster):
        self.set_context(context)
        self.logger.info('identity action: *do* completed')


class FailureAction(AbstractAction):
    """ this class is intended to be used by Unit Tests """
    def __init__(self, **kwargs):
        super(FailureAction, self).__init__('Failure Action', kwargs)

    def do(self, context, execution_cluster):
        self.set_context(context)
        raise UserWarning('failure action: raising exception')
