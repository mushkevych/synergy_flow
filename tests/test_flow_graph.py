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
from flow.core.flow_graph_node import FlowGraphNode
from flow.core.execution_context import get_logger, ExecutionContext
from flow.core.ephemeral_cluster import EphemeralCluster

TEST_PRESET_TIMEPERIOD = '2016060107'


class FlowGraphTest(unittest.TestCase):
    def setUp(self):
        self.context = ExecutionContext(TEST_PRESET_TIMEPERIOD, settings.settings)
        self.logger = get_logger('unit_test', self.context)

    def tearDown(self):
        pass

    @mock.patch('flow.core.flow_graph.FlowDao')
    def test_set_context(self, mock_flow_dao):
        """
        flow_dao is mocked to prevent performing
        read/write operations on the DB
        as this UT is about testing the iterator logic
        """
        the_flow = flows.flows[ut_flows.UNIT_TEST_FLOW_SIMPLE]

        self.assertIsNone(the_flow.context)
        the_flow.set_context(self.context)
        self.assertIsNotNone(the_flow.context)

    @mock.patch('flow.core.flow_graph.FlowDao')
    @mock.patch('flow.core.flow_graph.StepDao')
    @mock.patch('flow.core.flow_graph_node.StepDao')
    def test_simple_iterator(self, flow_flow_dao, flow_step_dao, step_step_dao):
        """ method tests happy-flow for the iterator """
        the_flow = flows.flows[ut_flows.UNIT_TEST_FLOW_SIMPLE]
        the_flow.mark_start(self.context)

        steps_order = list()
        for step_name in the_flow:
            steps_order.append(step_name)
            step = the_flow[step_name]
            assert isinstance(step, FlowGraphNode)

            step.set_context(self.context)
            step.mark_start()
            step.step_instance.is_pre_completed = True
            step.step_instance.is_main_completed = True
            step.step_instance.is_post_completed = True
            step.mark_success()

        self.assertListEqual(steps_order, ['step_1', 'step_2', 'step_3', 'step_4', 'step_5'])

    @mock.patch('flow.core.flow_graph.FlowDao')
    @mock.patch('flow.core.flow_graph.StepDao')
    @mock.patch('flow.core.flow_graph_node.StepDao')
    def test_interrupted_iterator(self, flow_flow_dao, flow_step_dao, step_step_dao):
        """ method tests iterator interrupted by failed step """
        the_flow = flows.flows[ut_flows.UNIT_TEST_FLOW_FAILURE]
        the_flow.mark_start(self.context)
        ephemeral_cluster = EphemeralCluster('unit test cluster', self.context)

        steps_order = list()
        for step_name in the_flow:
            steps_order.append(step_name)
            step = the_flow[step_name]
            assert isinstance(step, FlowGraphNode)
            step.run(self.context, ephemeral_cluster)

        self.assertListEqual(steps_order, ['step_1', 'step_2', 'step_3', 'step_4'])


if __name__ == '__main__':
    unittest.main()
