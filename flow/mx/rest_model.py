__author__ = 'Bohdan Mushkevych'

from odm.fields import BooleanField, StringField, DictField, ListField, NestedDocumentField, IntegerField
from odm.document import BaseDocument

from flow.db.model.flow import Flow
from flow.db.model.step import Step


FIELD_ACTION_NAME = 'action_name'
FIELD_ACTION_KWARGS = 'kwargs'
FIELD_STATE = 'state'
FIELD_PRE_ACTIONSET = 'pre_actionset'
FIELD_MAIN_ACTIONSET = 'main_actionset'
FIELD_POST_ACTIONSET = 'post_actionset'
FIELD_ACTIONS = 'actions'
FIELD_STEPS = 'steps'
FIELD_GRAPH = 'graph'
FIELD_PREVIOUS_NODES = 'previous_nodes'
FIELD_NEXT_NODES = 'next_nodes'
FIELD_DURATION = 'duration'


class RestAction(BaseDocument):
    action_name = StringField(FIELD_ACTION_NAME)
    kwargs = DictField(FIELD_ACTION_KWARGS)


class RestActionset(BaseDocument):
    state = StringField(FIELD_STATE)
    actions = ListField(FIELD_ACTIONS)


class RestStep(Step):
    pre_actionset = NestedDocumentField(FIELD_PRE_ACTIONSET, RestActionset)
    main_actionset = NestedDocumentField(FIELD_MAIN_ACTIONSET, RestActionset)
    post_actionset = NestedDocumentField(FIELD_POST_ACTIONSET, RestActionset)
    duration = IntegerField(FIELD_DURATION)

    previous_nodes = ListField(FIELD_PREVIOUS_NODES)
    next_nodes = ListField(FIELD_NEXT_NODES)


class RestFlow(Flow):
    # format {step_name: RestStep }
    steps = DictField(FIELD_STEPS)

    # format {step_name: RestStep }
    # copy of *RestFlow.steps* with additional *start* and *finish* steps
    graph = DictField(FIELD_GRAPH)
