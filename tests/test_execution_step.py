__author__ = 'Bohdan Mushkevych'

import unittest

from synergy.conf import settings

from flow.core.ephemeral_cluster import EphemeralCluster
from flow.core.execution_context import get_logger, ExecutionContext
from flow.core.execution_step import ExecutionStep
from flow.core.simple_actions import FailureAction, IdentityAction

TEST_PRESET_TIMEPERIOD = '2016060107'


class FlowGraphTest(unittest.TestCase):
    def setUp(self):
        self.context = ExecutionContext(TEST_PRESET_TIMEPERIOD, settings.settings)
        self.logger = get_logger('unit_test', self.context)
        self.ephemeral_cluster = EphemeralCluster('unit test cluster', self.context)

    def tearDown(self):
        pass

    def test_simple_step(self):
        """ method tests happy-flow for the execution flow """
        sa_identity = IdentityAction()
        exec_step = ExecutionStep(name='a step',
                                  main_action=sa_identity,
                                  pre_actions=[sa_identity],
                                  post_actions=[sa_identity])
        exec_step.set_context(self.context)

        self.assertFalse(exec_step.is_complete)
        self.assertFalse(exec_step.is_pre_completed)
        is_success = exec_step.do_pre(self.context, self.ephemeral_cluster)
        self.assertTrue(is_success)
        self.assertFalse(exec_step.is_complete)
        self.assertTrue(exec_step.is_pre_completed)

        self.assertFalse(exec_step.is_main_completed)
        is_success = exec_step.do_main(self.context, self.ephemeral_cluster)
        self.assertTrue(is_success)
        self.assertFalse(exec_step.is_complete)
        self.assertTrue(exec_step.is_main_completed)

        self.assertFalse(exec_step.is_post_completed)
        is_success = exec_step.do_post(self.context, self.ephemeral_cluster)
        self.assertTrue(is_success)
        self.assertTrue(exec_step.is_post_completed)

    def test_failing_step(self):
        """ method tests execution step, where one of the phases is failing """
        sa_identity = IdentityAction()
        sa_failure = FailureAction()
        exec_step = ExecutionStep(name='a step',
                                  main_action=sa_failure,
                                  pre_actions=[sa_identity],
                                  post_actions=[sa_identity])
        exec_step.set_context(self.context)

        self.assertFalse(exec_step.is_complete)
        self.assertFalse(exec_step.is_pre_completed)
        is_success = exec_step.do_pre(self.context, self.ephemeral_cluster)
        self.assertTrue(is_success)
        self.assertFalse(exec_step.is_complete)
        self.assertTrue(exec_step.is_pre_completed)

        self.assertFalse(exec_step.is_main_completed)
        is_success = exec_step.do_main(self.context, self.ephemeral_cluster)
        self.assertFalse(is_success)
        self.assertFalse(exec_step.is_complete)
        self.assertFalse(exec_step.is_main_completed)

        self.assertFalse(exec_step.is_post_completed)
        is_success = exec_step.do_post(self.context, self.ephemeral_cluster)
        self.assertTrue(is_success)
        self.assertTrue(exec_step.is_post_completed)


if __name__ == '__main__':
    unittest.main()
