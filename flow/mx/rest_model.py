__author__ = 'Bohdan Mushkevych'

from odm.fields import BooleanField, StringField, DictField, ListField, NestedDocumentField
from odm.document import BaseDocument

from flow.db.model.flow import Flow
from flow.db.model.step import Step


FIELD_IS_ALIVE = 'is_alive'                 # actual state of the trigger
FIELD_NEXT_RUN_IN = 'next_run_in'           # duration until the next trigger event in HH:MM:SS format
FIELD_NEXT_TIMEPERIOD = 'next_timeperiod'   # Synergy timeperiod format
FIELD_DEPENDANT_TREES = 'dependant_trees'
FIELD_SORTED_PROCESS_NAMES = 'sorted_process_names'     # process names sorted by their time_qualifier
FIELD_REPROCESSING_QUEUE = 'reprocessing_queue'

FIELD_NUMBER_OF_CHILDREN = 'number_of_children'
FIELD_PROCESSES = 'processes'
FIELD_TIME_QUALIFIER = 'time_qualifier'
FIELD_STEPS = 'steps'
FIELD_FLOW = 'flow'


class RestFlow(Flow):
    is_alive = BooleanField(FIELD_IS_ALIVE)
    next_run_in = StringField(FIELD_NEXT_RUN_IN)


class RestStep(Step):
    is_alive = BooleanField(FIELD_IS_ALIVE)
    next_run_in = StringField(FIELD_NEXT_RUN_IN)
    next_timeperiod = StringField(FIELD_NEXT_TIMEPERIOD)
    reprocessing_queue = ListField(FIELD_REPROCESSING_QUEUE)


class RestFlowGraph(BaseDocument):
    flow = NestedDocumentField(FIELD_FLOW, RestFlow, null=True)
    steps = DictField(FIELD_STEPS)


class RestFlowGraphNode(BaseDocument):
    flow = NestedDocumentField(FIELD_FLOW, RestStep, null=True)
    steps = DictField(FIELD_STEPS)
