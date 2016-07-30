__author__ = 'Bohdan Mushkevych'

from odm.fields import BooleanField, StringField, DictField, ListField, NestedDocumentField, IntegerField
from odm.document import BaseDocument

from flow.db.model.flow import Flow
from flow.db.model.step import Step


FIELD_ACTION_NAME = 'action_name'
FIELD_ACTION_KWARGS = 'kwargs'
FIELD_IS_PRE_COMPLETED = 'is_pre_completed'
FIELD_IS_MAIN_COMPLETED = 'is_main_completed'
FIELD_IS_POST_COMPLETED = 'is_post_completed'
FIELD_PRE_ACTIONS = 'pre_actions'
FIELD_MAIN_ACTION = 'main_action'
FIELD_POST_ACTIONS = 'post_actions'
FIELD_STEPS = 'steps'
FIELD_GRAPH = 'graph'
FIELD_PREVIOUS_NODES = 'previous_nodes'
FIELD_NEXT_NODES = 'next_nodes'
FIELD_DURATION = 'duration'


class RestAction(BaseDocument):
    action_name = StringField(FIELD_ACTION_NAME)
    kwargs = DictField(FIELD_ACTION_KWARGS)


class RestStep(Step):
    is_pre_completed = BooleanField(FIELD_IS_PRE_COMPLETED)
    is_main_completed = BooleanField(FIELD_IS_MAIN_COMPLETED)
    is_post_completed = BooleanField(FIELD_IS_POST_COMPLETED)
    duration = IntegerField(FIELD_DURATION)

    pre_actions = ListField(FIELD_PRE_ACTIONS)
    main_action = NestedDocumentField(FIELD_MAIN_ACTION, RestAction, null=True)
    post_actions = ListField(FIELD_POST_ACTIONS)

    previous_nodes = ListField(FIELD_PREVIOUS_NODES)
    next_nodes = ListField(FIELD_NEXT_NODES)


class RestFlow(Flow):
    # format {step_name: RestStep }
    steps = DictField(FIELD_STEPS)

    # format {step_name: RestStep }
    # copy of *RestFlow.steps* with additional *start* and *finish* steps
    graph = DictField(FIELD_GRAPH)
