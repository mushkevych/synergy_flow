__author__ = 'Bohdan Mushkevych'

from flow.abstract_action import AbstractAction


def validate_action_param(param, klass):
    if isinstance(param, (tuple, list)):
        assert all(isinstance(p, klass) for p in param), \
            'Expected parameters of either {0} or list of {0}. Instead got {1}' \
                .format(klass.__name__, param.__class__.__name__)
    else:
        assert isinstance(param, klass), 'Expected parameters of either {0} or list of {0}. Instead got {1}' \
            .format(klass.__name__, param.__class__.__name__)


class ExecutionStep(object):
    def __init__(self, name, main_action, pre_actions=None, post_actions=None, kwargs=None):
        self.name = name
        self.main_action = main_action

        self.is_pre_completed = False
        self.is_main_completed = False
        self.is_post_completed = False

        self.pre_actions = [] if not pre_actions else pre_actions
        validate_action_param(self.pre_actions, AbstractAction)

        self.post_actions = [] if not post_actions else post_actions
        validate_action_param(self.post_actions, AbstractAction)

        self.kwargs = {} if not kwargs else kwargs

    @property
    def is_complete(self):
        return self.is_pre_completed and self.is_main_completed and self.is_post_completed

    def _do(self, actions):
        is_success = True
        for action in actions:
            try:
                action.do()
            except:
                is_success = False
                break
            finally:
                action.cleanup()
        return is_success

    def do_pre(self):
        self.is_pre_completed = self._do(self.pre_actions)

    def do_main(self):
        self.is_main_completed = self._do([self.main_action])

    def do_post(self):
        self.is_post_completed = self._do(self.post_actions)
