__author__ = 'Bohdan Mushkevych'

from odm.document import BaseDocument
from odm.fields import StringField, ObjectIdField, DateTimeField


# Step record created in the DB
# Next valid states: STATE_IN_PROGRESS
STATE_EMBRYO = 'state_embryo'

# Step execution started by a worker
STATE_IN_PROGRESS = 'state_in_progress'

# Step was successfully processed by the worker
STATE_PROCESSED = 'state_processed'

# Job has been manually marked as SKIPPED via MX
# all non-completed Steps are marked as STATE_CANCELED
STATE_CANCELED = 'state_canceled'

# Step has failed with an exception during the execution
STATE_INVALID = 'state_invalid'

# Step was completed, but no data was found to process
STATE_NOOP = 'state_noop'


class Step(BaseDocument):
    """ Module represents persistent Model for a single step in a flow """

    db_id = ObjectIdField(name='_id', null=True)
    flow_name = StringField()
    step_name = StringField()
    timeperiod = StringField(null=True)
    state = StringField(choices=[STATE_INVALID, STATE_EMBRYO, STATE_IN_PROGRESS,
                                 STATE_PROCESSED, STATE_CANCELED, STATE_NOOP])
    created_at = DateTimeField()
    started_at = DateTimeField()
    finished_at = DateTimeField()

    related_flow = ObjectIdField()

    @classmethod
    def key_fields(cls):
        return cls.flow_name.name, cls.step_name.name, cls.timeperiod.name

    @property
    def is_failed(self):
        return self.state in [STATE_INVALID, STATE_CANCELED]

    @property
    def is_processed(self):
        return self.state == STATE_PROCESSED

    @property
    def is_in_progress(self):
        return self.state == STATE_IN_PROGRESS


TIMEPERIOD = Step.timeperiod.name
FLOW_NAME = Step.flow_name.name
STEP_NAME = Step.step_name.name
RELATED_FLOW = Step.related_flow.name
