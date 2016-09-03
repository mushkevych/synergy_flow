__author__ = 'Bohdan Mushkevych'

from synergy.conf import settings, context
from synergy.db.model import unit_of_work
from synergy.db.model.unit_of_work import TYPE_MANAGED
from synergy.workers.abstract_uow_aware_worker import AbstractUowAwareWorker

from flow.core.execution_context import ExecutionContext
from flow.core.execution_engine import ExecutionEngine
from flow.db.model import flow
from flow.db.model.flow import RUN_MODE_NOMINAL, RUN_MODE_RECOVERY
from flow.db.dao.flow_dao import FlowDao
from flow.flow_constants import *


class FlowDriver(AbstractUowAwareWorker):
    """starts Synergy Flow processing job, supervises its execution and updates unit_of_work"""

    def __init__(self, process_name):
        super(FlowDriver, self).__init__(process_name, perform_db_logging=True)
        self.flow_dao = FlowDao(self.logger)

    def _process_uow(self, uow):
        flow_name = uow.arguments[ARGUMENT_FLOW_NAME]
        if uow.unit_of_work_type == TYPE_MANAGED:
            run_mode = self.flow_dao.managed_run_mode(self.process_name, flow_name, uow.timeperiod)
        else:
            run_mode = uow.arguments.get(ARGUMENT_RUN_MODE)

        try:
            self.logger.info('starting Flow: {0} {{'.format(flow_name))
            execution_engine = ExecutionEngine(self.logger, flow_name)

            context = ExecutionContext(flow_name, uow.timeperiod, uow.start_timeperiod, uow.end_timeperiod,
                                       settings.settings)
            if run_mode == RUN_MODE_RECOVERY:
                execution_engine.recover(context)
            elif run_mode == RUN_MODE_RUN_ONE:
                step_name = uow.arguments.get(ARGUMENT_STEP_NAME)
                execution_engine.run_one(context, step_name)
            elif run_mode == RUN_MODE_RUN_FROM:
                step_name = uow.arguments.get(ARGUMENT_STEP_NAME)
                execution_engine.run_from(context, step_name)
            elif run_mode == RUN_MODE_NOMINAL:
                execution_engine.run(context)
            else:
                raise ValueError('run mode {0} is unknown to the Synergy Flow'.format(run_mode))

            if context.flow_entry.state == flow.STATE_PROCESSED:
                uow_status = unit_of_work.STATE_PROCESSED
            elif context.flow_entry.state == flow.STATE_NOOP:
                uow_status = unit_of_work.STATE_NOOP
            else:
                uow_status = unit_of_work.STATE_INVALID

        except Exception:
            self.logger.error('Exception on workflow execution: {0}'.format(flow_name), exc_info=True)
            uow_status = unit_of_work.STATE_INVALID
        finally:
            self.logger.info('}')
        return 0, uow_status
