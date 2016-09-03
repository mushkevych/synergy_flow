__author__ = 'Bohdan Mushkevych'

from odm.document import BaseDocument
from odm.fields import StringField, ObjectIdField, DateTimeField

TIMEPERIOD = 'timeperiod'
START_TIMEPERIOD = 'start_timeperiod'
END_TIMEPERIOD = 'end_timeperiod'
FLOW_NAME = 'flow_name'
STATE = 'state'

CREATED_AT = 'created_at'
STARTED_AT = 'started_at'
FINISHED_AT = 'finished_at'

RUN_MODE = 'run_mode'
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

    db_id = ObjectIdField('_id', null=True)
    flow_name = StringField(FLOW_NAME)
    timeperiod = StringField(TIMEPERIOD)
    start_timeperiod = StringField(START_TIMEPERIOD)
    end_timeperiod = StringField(END_TIMEPERIOD)
    state = StringField(STATE, choices=[STATE_EMBRYO, STATE_IN_PROGRESS, STATE_PROCESSED, STATE_NOOP, STATE_INVALID])

    # run_mode override rules:
    # - default value is read from ProcessEntry.arguments['run_mode']
    # - if the ProcessEntry.arguments['run_mode'] is None then run_mode is assumed `run_mode_nominal`
    # - Flow.run_mode, if specified, overrides ProcessEntry.arguments['run_mode']
    # - UOW.arguments['run_mode'] overrides Flow.run_mode
    run_mode = StringField(RUN_MODE, choices=[RUN_MODE_NOMINAL, RUN_MODE_RECOVERY])

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
