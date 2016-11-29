__author__ = 'Bohdan Mushkevych'

import copy
from flow.core.abstract_action import AbstractAction
from flow.core.execution_context import ContextDriven, get_step_logger, valid_context

# NOTICE: actionset states carry different names (pending vs embryo, etc),
# as they have no persistence and have different CSS coloring schema
ACTIONSET_PENDING = 'actionset_pending'
ACTIONSET_RUNNING = 'actionset_running'
ACTIONSET_COMPLETE = 'actionset_complete'
ACTIONSET_FAILED = 'actionset_failed'


def validate_action_param(param, klass):
    assert isinstance(param, (tuple, list)), \
        'Expected list of {0} or an empty list. Instead got {1}'.format(klass.__name__, param.__class__.__name__)
    assert all(isinstance(p, klass) for p in param), \
        'Expected list of {0}. Not all elements of the list were of this type'.format(klass.__name__)


class Actionset(ContextDriven):
    """ set of Actions to be performed together """
    def __init__(self, actions, step_name):
        super(Actionset, self).__init__()
        if actions is None: actions = []
        validate_action_param(actions, AbstractAction)

        self.step_name = step_name
        self.actions = copy.deepcopy(actions)
        self.state = ACTIONSET_PENDING

    def get_logger(self):
        return get_step_logger(self.flow_name, self.step_name, self.settings)

    @valid_context
    def do(self, execution_cluster):
        self.state = ACTIONSET_RUNNING
        for action in self.actions:
            try:
                action.set_context(self.context, step_name=self.step_name)
                action.do(execution_cluster)
            except Exception as e:
                self.state = ACTIONSET_FAILED
                self.logger.error('Execution Error: {0}'.format(e), exc_info=True)
                raise
            finally:
                action.cleanup()
        self.state = ACTIONSET_COMPLETE


class StepExecutor(ContextDriven):
    """ Step runner class for the GraphNode, encapsulating means to run and track execution progress
        NOTICE: during __init__ all actions are cloned
                so that set_context can be applied to an action in concurrency-safe manner """
    def __init__(self, step_name, main_action, pre_actions=None, post_actions=None, skip=False):
        super(StepExecutor, self).__init__()
        assert isinstance(main_action, AbstractAction)

        self.step_name = step_name
        self.pre_actionset = Actionset(pre_actions, step_name)
        self.main_actionset = Actionset([main_action], step_name)
        self.post_actionset = Actionset(post_actions, step_name)
        self.skip = skip

    def get_logger(self):
        return get_step_logger(self.flow_name, self.step_name, self.settings)

    @property
    def is_complete(self):
        return self.pre_actionset.state == ACTIONSET_COMPLETE \
               and self.main_actionset.state == ACTIONSET_COMPLETE \
               and self.post_actionset.state == ACTIONSET_COMPLETE

    @valid_context
    def do(self, execution_cluster):
        if self.skip:
            for block in [self.pre_actionset, self.main_actionset, self.post_actionset]:
                block.state.is_success = ACTIONSET_COMPLETE
            return

        try:
            for block in [self.pre_actionset, self.main_actionset, self.post_actionset]:
                block.set_context(self.context)
                block.do(execution_cluster)
        except Exception as e:
            pass
