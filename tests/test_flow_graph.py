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
from flow.core.execution_context import ExecutionContext
from flow.core.ephemeral_cluster import EphemeralCluster

TEST_PRESET_TIMEPERIOD = '2016060107'
TEST_START_TIMEPERIOD = '2016060107'
TEST_END_TIMEPERIOD = '2016060108'


class FlowGraphTest(unittest.TestCase):
    def setUp(self):
        flow_name = 'ut_flow_name'
        self.context = ExecutionContext(flow_name, TEST_PRESET_TIMEPERIOD, TEST_START_TIMEPERIOD, TEST_END_TIMEPERIOD,
                                        settings.settings)

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
    @mock.patch('flow.core.flow_graph.LogRecordingHandler')
    @mock.patch('flow.core.flow_graph_node.LogRecordingHandler')
    def test_simple_iterator(self, flow_flow_dao, flow_step_dao, step_step_dao,
                             flow_recording_handler, step_recording_handler):
        """ method tests happy-flow for the iterator """
        the_flow = flows.flows[ut_flows.UNIT_TEST_FLOW_SIMPLE]
        the_flow.set_context(self.context)
        the_flow.mark_start()

        steps_order = list()
        for step_name in the_flow:
            steps_order.append(step_name)
            step = the_flow[step_name]
            assert isinstance(step, FlowGraphNode)

            step.set_context(self.context)
            step.mark_start()
            step.step_executor.is_pre_completed = True
            step.step_executor.is_main_completed = True
            step.step_executor.is_post_completed = True
            step.mark_success()

        self.assertListEqual(steps_order, ['step_1', 'step_2', 'step_3', 'step_4',
                                           'step_5', 'step_6', 'step_7', 'step_8'])

    @mock.patch('flow.core.flow_graph.FlowDao')
    @mock.patch('flow.core.flow_graph.StepDao')
    @mock.patch('flow.core.flow_graph_node.StepDao')
    @mock.patch('flow.core.flow_graph.LogRecordingHandler')
    @mock.patch('flow.core.flow_graph_node.LogRecordingHandler')
    def test_interrupted_iterator(self, flow_flow_dao, flow_step_dao, step_step_dao,
                                  flow_recording_handler, step_recording_handler):
        """ method tests iterator interrupted by failed step """
        the_flow = flows.flows[ut_flows.UNIT_TEST_FLOW_FAILURE]
        the_flow.set_context(self.context)
        the_flow.mark_start()
        ephemeral_cluster = EphemeralCluster('unit test cluster', self.context)

        steps_order = list()
        for step_name in the_flow:
            steps_order.append(step_name)
            step = the_flow[step_name]
            assert isinstance(step, FlowGraphNode)
            step.set_context(self.context)
            step.run(ephemeral_cluster)

        self.assertListEqual(steps_order, ['step_1', 'step_2', 'step_3', 'step_4'])

    def test_all_dependant_steps(self):
        """ method verifies if iterator interrupted by failed step """
        the_flow = flows.flows[ut_flows.UNIT_TEST_FLOW_SIMPLE]
        self.assertSetEqual(set(the_flow.all_dependant_steps('step_1')),
                            {'step_2', 'step_3', 'step_4', 'step_5', 'step_6', 'step_7', 'step_8'})
        self.assertSetEqual(set(the_flow.all_dependant_steps('step_2')),
                            {'step_3', 'step_4', 'step_5', 'step_6', 'step_7', 'step_8'})
        self.assertSetEqual(set(the_flow.all_dependant_steps('step_3')), {'step_5'})
        self.assertSetEqual(set(the_flow.all_dependant_steps('step_6')), {'step_7', 'step_8'})


if __name__ == '__main__':
    unittest.main()
