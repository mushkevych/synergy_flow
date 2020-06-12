__author__ = 'Bohdan Mushkevych'

from odm.document import BaseDocument
from odm.fields import StringField, ObjectIdField, DateTimeField

RUN_MODE_NOMINAL = 'run_mode_nominal'
RUN_MODE_RECOVERY = 'run_mode_recovery'

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
STATE_EMBRYO = 'state_embryo'


class Flow(BaseDocument):
    """ class presents status for a Flow run """

    db_id = ObjectIdField(name='_id', null=True)
    flow_name = StringField()
    timeperiod = StringField()
    start_timeperiod = StringField()
    end_timeperiod = StringField()
    state = StringField(choices=[STATE_EMBRYO, STATE_IN_PROGRESS, STATE_PROCESSED, STATE_NOOP, STATE_INVALID])

    # run_mode override rules:
    # - default value is read from ProcessEntry.arguments['run_mode']
    # - if the ProcessEntry.arguments['run_mode'] is None then run_mode is assumed `run_mode_nominal`
    # - Flow.run_mode, if specified, overrides ProcessEntry.arguments['run_mode']
    # - UOW.arguments['run_mode'] overrides Flow.run_mode
    run_mode = StringField(choices=[RUN_MODE_NOMINAL, RUN_MODE_RECOVERY])

    created_at = DateTimeField()
    started_at = DateTimeField()
    finished_at = DateTimeField()

    @classmethod
    def key_fields(cls):
        return cls.flow_name.name, cls.timeperiod.name


TIMEPERIOD = Flow.timeperiod.name
FLOW_NAME = Flow.flow_name.name
