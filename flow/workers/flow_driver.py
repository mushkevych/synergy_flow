__author__ = 'Bohdan Mushkevych'

from flow.conf import flows
from flow.core.execution_context import ExecutionContext
from flow.core.execution_engine import ExecutionEngine
from synergy.conf import settings
from synergy.db.model import unit_of_work
from synergy.workers.abstract_uow_aware_worker import AbstractUowAwareWorker

from flow.db.model import flow

ARGUMENT_FLOW_NAME = 'flow_name'


class FlowDriver(AbstractUowAwareWorker):
    """starts Synergy Flow processing job, supervises its execution and updates unit_of_work"""

    def __init__(self, process_name):
        super(FlowDriver, self).__init__(process_name)

    def _process_uow(self, uow):
        flow_name = uow.arguments[ARGUMENT_FLOW_NAME]
        try:
            self.logger.info('starting Flow: {0} {{'.format(flow_name))

            flow_graph = flows.get(flow_name)
            execution_engine = ExecutionEngine(self.logger, flow_graph)

            context = ExecutionContext(flow_name, uow.timeperiod, settings.settings)
            execution_engine.run(context)

            if context.flow_model.state == flow.STATE_PROCESSED:
                uow_status = unit_of_work.STATE_PROCESSED
            elif context.flow_model.state == flow.STATE_NOOP:
                uow_status = unit_of_work.STATE_NOOP
            else:
                uow_status = unit_of_work.STATE_INVALID

        except Exception:
            self.logger.error('Exception on flow execution: {0}'.format(flow_name), exc_info=True)
            uow_status = unit_of_work.STATE_INVALID
        finally:
            self.logger.info('}')
        return 0, uow_status
