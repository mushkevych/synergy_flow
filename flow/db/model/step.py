__author__ = 'Bohdan Mushkevych'

from odm.document import BaseDocument
from odm.fields import StringField, ObjectIdField, DateTimeField

TIMEPERIOD = 'timeperiod'
STATE = 'state'
CREATED_AT = 'created_at'
STARTED_AT = 'started_at'
FINISHED_AT = 'finished_at'

FLOW_NAME = 'flow_name'
STEP_NAME = 'step_name'

RELATED_FLOW = 'related_flow'

# Step record created in the DB
# Next valid states: STATE_IN_PROGRESS
STATE_REQUESTED = 'state_requested'

# Step execution started by a worker
STATE_IN_PROGRESS = 'state_in_progress'

# Step was successfully processed by the worker
STATE_PROCESSED = 'state_processed'

# Job has been manually marked as SKIPPED via MX
# all non-completed Steps are marked as STATE_CANCELED
STATE_CANCELED = 'state_canceled'

# Step has failed with an exception at the worker level
STATE_INVALID = 'state_invalid'

# Step was completed, but no data was found to process
STATE_NOOP = 'state_noop'


class Step(BaseDocument):
    """ Module represents persistent Model for a single step in a flow """

    db_id = ObjectIdField('_id', null=True)
    flow_name = StringField(FLOW_NAME)
    step_name = StringField(STEP_NAME)
    timeperiod = StringField(TIMEPERIOD, null=True)
    state = StringField(STATE, choices=[STATE_INVALID, STATE_REQUESTED, STATE_IN_PROGRESS,
                                        STATE_PROCESSED, STATE_CANCELED, STATE_NOOP])
    created_at = DateTimeField(CREATED_AT)
    started_at = DateTimeField(STARTED_AT)
    finished_at = DateTimeField(FINISHED_AT)

    related_flow = ObjectIdField(RELATED_FLOW)

    @property
    def key(self):
        return self.flow_name, self.step_name, self.timeperiod

    @property
    def is_failed(self):
        return self.state in [STATE_INVALID, STATE_CANCELED]
