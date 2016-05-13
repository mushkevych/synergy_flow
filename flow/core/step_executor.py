__author__ = 'Bohdan Mushkevych'

import copy
from flow.core.abstract_action import AbstractAction
from flow.core.execution_context import ContextDriven, get_step_logger


def validate_action_param(param, klass):
    assert isinstance(param, (tuple, list)), \
        'Expected list of {0} or an empty list. Instead got {1}'.format(klass.__name__, param.__class__.__name__)
    assert all(isinstance(p, klass) for p in param), \
        'Expected list of {0}. Not all elements of the list were of this type'.format(klass.__name__)


class StepExecutor(ContextDriven):
    """ helper class for the GraphNode, encapsulating means to run and track action progress
        NOTICE: during __init__ all actions are cloned
                so that set_context can be applied to an action in concurrency-safe manner """
    def __init__(self, step_name, main_action, pre_actions=None, post_actions=None):
        super(StepExecutor, self).__init__()

        if pre_actions is None: pre_actions = []
        if post_actions is None: post_actions = []

        self.step_name = step_name
        assert isinstance(main_action, AbstractAction)
        self.main_action = copy.deepcopy(main_action)

        self.is_pre_completed = False
        self.is_main_completed = False
        self.is_post_completed = False

        validate_action_param(pre_actions, AbstractAction)
        self.pre_actions = copy.deepcopy(pre_actions)

        validate_action_param(post_actions, AbstractAction)
        self.post_actions = copy.deepcopy(post_actions)

    def get_logger(self):
        return get_step_logger(self.flow_name, self.step_name, self.settings)

    @property
    def is_complete(self):
        return self.is_pre_completed and self.is_main_completed and self.is_post_completed

    def _do(self, actions, execution_cluster):
        assert self.is_context_set is True
        is_success = True
        for action in actions:
            try:
                action.set_context(self.context, step_name=self.step_name)
                action.do(execution_cluster)
            except Exception as e:
                is_success = False
                self.logger.error('Execution Error: {0}'.format(e), exc_info=True)
                break
            finally:
                action.cleanup()
        return is_success

    def do_pre(self, execution_cluster):
        self.is_pre_completed = self._do(self.pre_actions, execution_cluster)
        return self.is_pre_completed

    def do_main(self, execution_cluster):
        self.is_main_completed = self._do([self.main_action], execution_cluster)
        return self.is_main_completed

    def do_post(self, execution_cluster):
        self.is_post_completed = self._do(self.post_actions, execution_cluster)
        return self.is_post_completed
