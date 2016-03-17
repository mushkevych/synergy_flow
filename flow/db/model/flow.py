__author__ = 'Bohdan Mushkevych'

from odm.document import BaseDocument
from odm.fields import StringField, ObjectIdField, DictField, DateTimeField

TIMEPERIOD = 'timeperiod'
FLOW_NAME = 'flow_name'
STATE = 'state'

CREATED_AT = 'created_at'
STARTED_AT = 'started_at'
FINISHED_AT = 'finished_at'

# Flow can get into STATE_INVALID if:
# a. related Job was marked for reprocessing via MX
# b. have failed with an exception at the step level
# NOTICE: FlowDriver changes STATE_INVALID -> STATE_IN_PROGRESS during re-posting
STATE_INVALID = 'state_invalid'

# given Flow was successfully executed
# This is a final state
STATE_PROCESSED = 'state_processed'

# given Flow had no steps to process
# This is a final state
STATE_NOOP = 'state_noop'

# FlowDriver triggers the flow execution.
# Next valid states: STATE_NOOP, STATE_PROCESSED, STATE_INVALID
STATE_IN_PROGRESS = 'state_in_progress'

# Flow record created in the DB
# Next valid states: STATE_IN_PROGRESS
STATE_REQUESTED = 'state_requested'


class Flow(BaseDocument):
    """ class presents status for a Flow run """

    db_id = ObjectIdField('_id', null=True)
    flow_name = StringField(FLOW_NAME)
    timeperiod = StringField(TIMEPERIOD)
    state = StringField(STATE, choices=[STATE_REQUESTED, STATE_IN_PROGRESS, STATE_PROCESSED, STATE_NOOP, STATE_INVALID])

    created_at = DateTimeField(CREATED_AT)
    started_at = DateTimeField(STARTED_AT)
    finished_at = DateTimeField(FINISHED_AT)

    @BaseDocument.key.getter
    def key(self):
        return self.flow_name, self.timeperiod

    @key.setter
    def key(self, value):
        """ :param value: tuple (name of the flow, timeperiod as string in Synergy Data format) """
        self.flow_name = value[0]
        self.timeperiod = value[1]
