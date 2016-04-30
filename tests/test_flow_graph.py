__author__ = 'Bohdan Mushkevych'

import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from tests import ut_flows
ut_flows.register_flows()

from synergy.conf import settings
from flow.conf import flows

from flow.core.flow_graph import FlowGraph
from flow.core.flow_graph_node import FlowGraphNode
from flow.core.execution_context import get_logger, ExecutionContext

TEST_PRESET_TIMEPERIOD = '2016060107'
TEST_PRESET_END_TIMEPERIOD = '2016060108'


class FlowGraphTest(unittest.TestCase):
    def setUp(self):
        self.context = ExecutionContext(TEST_PRESET_TIMEPERIOD, TEST_PRESET_END_TIMEPERIOD, settings.settings)
        self.logger = get_logger('unit_test', self.context)

    def tearDown(self):
        pass

    @mock.patch('flow.db.dao.flow_dao.FlowDao')
    def test_set_context(self, mock_flow_dao):
        """
        flow_dao is mocked to prevent performing
        read/write operations on the DB
        as this UT is about testing the iterator logic
        """
        the_flow = flows.get(ut_flows.UNIT_TEST_FLOW_SIMPLE)
        the_flow.set_context(self.context)

    def test_simple_iterator(self):
        """ method tests happy-flow of the iterator """
        the_flow = flows.get(ut_flows.UNIT_TEST_FLOW_SIMPLE)

        steps_order = list()
        for step in the_flow:
            steps_order.append(step)

        self.assertListEqual(steps_order, ['step_1', 'step_2', 'step_3', 'step_4', 'step_5'])


if __name__ == '__main__':
    unittest.main()
