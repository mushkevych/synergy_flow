__author__ = 'Bohdan Mushkevych'

from synergy.conf import context
from synergy.db.dao.base_dao import BaseDao
from flow.flow_constants import COLLECTION_FLOW, ARGUMENT_RUN_MODE
from flow.db.model.flow import Flow, FLOW_NAME, TIMEPERIOD, RUN_MODE_NOMINAL


class FlowDao(BaseDao):
    """ Thread-safe Data Access Object for *flow* table/collection """

    def __init__(self, logger):
        super(FlowDao, self).__init__(logger=logger,
                                      model_class=Flow,
                                      primary_key=[FLOW_NAME, TIMEPERIOD],
                                      collection_name=COLLECTION_FLOW)

    def managed_run_mode(self, process_name, flow_name, timeperiod):
        """ managed `run mode` is defined globally at ProcessEntry.arguments['run_mode']
            however, can be overridden locally at Flow.run_mode
            This method takes burden of checking both places and returning valid `run mode`"""

        # retrieve default run_mode value from the process_context
        process_entry = context.process_context[process_name]
        run_mode = process_entry.arguments.get(ARGUMENT_RUN_MODE, RUN_MODE_NOMINAL)

        try:
            # fetch existing Flow from the DB
            # if present, run_mode overrides default one
            db_key = [flow_name, timeperiod]
            flow_entry = self.get_one(db_key)
            run_mode = flow_entry.run_mode
        except LookupError:
            # no flow record for given key was present in the database
            # use default one
            pass
        return run_mode
