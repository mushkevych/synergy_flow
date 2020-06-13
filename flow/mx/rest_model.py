__author__ = 'Bohdan Mushkevych'

from odm.fields import StringField, DictField, ListField, NestedDocumentField, IntegerField
from odm.document import BaseDocument

from flow.db.model.flow import Flow
from flow.db.model.step import Step


class RestAction(BaseDocument):
    action_name = StringField()
    kwargs = DictField()


class RestActionset(BaseDocument):
    state = StringField()
    actions = ListField()


class RestStep(Step):
    pre_actionset = NestedDocumentField(RestActionset)
    main_actionset = NestedDocumentField(RestActionset)
    post_actionset = NestedDocumentField(RestActionset)
    duration = IntegerField()

    previous_nodes = ListField()
    next_nodes = ListField()


class RestFlow(Flow):
    # format {step_name: RestStep }
    steps = DictField()

    # format {step_name: RestStep }
    # copy of *RestFlow.steps* with additional *start* and *finish* steps
    graph = DictField()


FIELD_PREVIOUS_NODES = RestStep.previous_nodes.name
FIELD_NEXT_NODES = RestStep.next_nodes.name
