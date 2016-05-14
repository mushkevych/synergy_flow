__author__ = 'Bohdan Mushkevych'

import unittest

from synergy.conf import settings

from flow.core.ephemeral_cluster import EphemeralCluster
from flow.core.execution_context import ExecutionContext
from flow.core.step_executor import StepExecutor
from flow.core.simple_actions import FailureAction, IdentityAction

TEST_PRESET_TIMEPERIOD = '2016060107'


class StepExecutorTest(unittest.TestCase):
    def setUp(self):
        flow_name = 'ut_flow_name'
        self.context = ExecutionContext(flow_name, TEST_PRESET_TIMEPERIOD, settings.settings)
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
        self.assertFalse(step_exec.is_pre_completed)
        is_success = step_exec.do_pre(self.ephemeral_cluster)
        self.assertTrue(is_success)
        self.assertFalse(step_exec.is_complete)
        self.assertTrue(step_exec.is_pre_completed)

        self.assertFalse(step_exec.is_main_completed)
        is_success = step_exec.do_main(self.ephemeral_cluster)
        self.assertTrue(is_success)
        self.assertFalse(step_exec.is_complete)
        self.assertTrue(step_exec.is_main_completed)

        self.assertFalse(step_exec.is_post_completed)
        is_success = step_exec.do_post(self.ephemeral_cluster)
        self.assertTrue(is_success)
        self.assertTrue(step_exec.is_post_completed)

    def test_failing_step(self):
        """ method tests execution step, where one of the phases is failing """
        sa_identity = IdentityAction()
        sa_failure = FailureAction()
        exec_step = StepExecutor(step_name='a step',
                                 main_action=sa_failure,
                                 pre_actions=[sa_identity],
                                 post_actions=[sa_identity])
        exec_step.set_context(self.context)

        self.assertFalse(exec_step.is_complete)
        self.assertFalse(exec_step.is_pre_completed)
        is_success = exec_step.do_pre(self.ephemeral_cluster)
        self.assertTrue(is_success)
        self.assertFalse(exec_step.is_complete)
        self.assertTrue(exec_step.is_pre_completed)

        self.assertFalse(exec_step.is_main_completed)
        is_success = exec_step.do_main(self.ephemeral_cluster)
        self.assertFalse(is_success)
        self.assertFalse(exec_step.is_complete)
        self.assertFalse(exec_step.is_main_completed)

        self.assertFalse(exec_step.is_post_completed)
        is_success = exec_step.do_post(self.ephemeral_cluster)
        self.assertTrue(is_success)
        self.assertTrue(exec_step.is_post_completed)


if __name__ == '__main__':
    unittest.main()
