__author__ = 'Bohdan Mushkevych'

import time
from flow.abstract_action import AbstractAction


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
