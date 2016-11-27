__author__ = 'Bohdan Mushkevych'

import unittest

from synergy.conf import settings

from flow.core.ephemeral_cluster import EphemeralCluster
from flow.core.execution_context import ExecutionContext
from flow.core.step_executor import StepExecutor, ACTIONSET_COMPLETE, ACTIONSET_FAILED, ACTIONSET_PENDING
from flow.core.simple_actions import FailureAction, IdentityAction

TEST_PRESET_TIMEPERIOD = '2016060107'
TEST_START_TIMEPERIOD = '2016060107'
TEST_END_TIMEPERIOD = '2016060108'


class StepExecutorTest(unittest.TestCase):
    def setUp(self):
        flow_name = 'ut_flow_name'
        self.context = ExecutionContext(flow_name, TEST_PRESET_TIMEPERIOD, TEST_START_TIMEPERIOD, TEST_END_TIMEPERIOD,
                                        settings.settings)
        self.ephemeral_cluster = EphemeralCluster('unit test cluster', self.context)

    def tearDown(self):
        pass

    def test_simple_step(self):
        """ method tests happy-flow for the execution flow """
        sa_identity = IdentityAction()
        step_exec = StepExecutor(step_name='a step',
                                 main_action=sa_identity,
                                 pre_actions=[sa_identity],
                                 post_actions=[sa_identity])
        step_exec.set_context(self.context)

        self.assertFalse(step_exec.is_complete)
        self.assertEqual(step_exec.pre_actionset.state, ACTIONSET_PENDING)
        self.assertEqual(step_exec.main_actionset.state, ACTIONSET_PENDING)
        self.assertEqual(step_exec.post_actionset.state, ACTIONSET_PENDING)
        step_exec.do(self.ephemeral_cluster)
        self.assertTrue(step_exec.is_complete)
        self.assertEqual(step_exec.pre_actionset.state, ACTIONSET_COMPLETE)
        self.assertEqual(step_exec.main_actionset.state, ACTIONSET_COMPLETE)
        self.assertEqual(step_exec.post_actionset.state, ACTIONSET_COMPLETE)

    def test_failing_step(self):
        """ method tests execution step, where one of the phases is failing """
        sa_identity = IdentityAction()
        sa_failure = FailureAction()
        step_exec = StepExecutor(step_name='a step',
                                 main_action=sa_failure,
                                 pre_actions=[sa_identity],
                                 post_actions=[sa_identity])
        step_exec.set_context(self.context)

        self.assertFalse(step_exec.is_complete)
        step_exec.do(self.ephemeral_cluster)
        self.assertFalse(step_exec.is_complete)
        self.assertEqual(step_exec.pre_actionset.state, ACTIONSET_COMPLETE)
        self.assertEqual(step_exec.main_actionset.state, ACTIONSET_FAILED)
        self.assertEqual(step_exec.post_actionset.state, ACTIONSET_PENDING)


if __name__ == '__main__':
    unittest.main()
