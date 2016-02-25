__author__ = 'Bohdan Mushkevych'

from flow.instantiable import Instantiable
from flow.abstract_action import AbstractAction
from flow.execution_context import ContextDriven


def validate_action_param(param, klass):
    if isinstance(param, (tuple, list)):
        assert all(isinstance(p, klass) for p in param), \
            'Expected parameters of either {0} or list of {0}. Instead got {1}' \
                .format(klass.__name__, param.__class__.__name__)
    else:
        assert isinstance(param, klass), 'Expected parameters of either {0} or list of {0}. Instead got {1}' \
            .format(klass.__name__, param.__class__.__name__)


class ExecutionStep(ContextDriven):
    def __init__(self, name, main_action, pre_actions=None, post_actions=None, kwargs=None):
        super(ExecutionStep, self).__init__(name)

        if pre_actions is None: pre_actions = []
        if post_actions is None: post_actions = []
        if kwargs is None: kwargs = {}

        self.name = name
        self.main_action = main_action

        self.is_pre_completed = False
        self.is_main_completed = False
        self.is_post_completed = False

        self.pre_actions = pre_actions
        validate_action_param(self.pre_actions, Instantiable)

        self.post_actions = post_actions
        validate_action_param(self.post_actions, Instantiable)

        self.kwargs = kwargs

    @property
    def is_complete(self):
        return self.is_pre_completed and self.is_main_completed and self.is_post_completed

    def _do(self, actions, context, execution_cluster):
        is_success = True
        for action_parameter in actions:
            assert isinstance(action_parameter, Instantiable)

            action = action_parameter.instantiate()
            assert isinstance(action, AbstractAction)

            try:
                action.do(context, execution_cluster)
            except:
                is_success = False
                break
            finally:
                action.cleanup()
        return is_success

    def do_pre(self, context, execution_cluster):
        self.is_pre_completed = self._do(self.pre_actions, context, execution_cluster)
        return self.is_pre_completed

    def do_main(self, context, execution_cluster):
        self.is_main_completed = self._do([self.main_action], context, execution_cluster)
        return self.is_main_completed

    def do_post(self, context, execution_cluster):
        self.is_post_completed = self._do(self.post_actions, context, execution_cluster)
        return self.is_post_completed
