__author__ = 'Bohdan Mushkevych'

from os import path
import unittest
try:
    # python 2.x
    import subprocess32 as subprocess
except ImportError:
    # python 3.3+
    import subprocess

from synergy.conf import settings
from flow.core.execution_context import ExecutionContext
from flow.core.ephemeral_cluster import EphemeralCluster

TEST_PRESET_TIMEPERIOD = '2016060107'
TEST_START_TIMEPERIOD = '2016060107'
TEST_END_TIMEPERIOD = '2016060108'


class EphemeralClusterTest(unittest.TestCase):
    def setUp(self):
        flow_name = 'ut_flow_name'
        self.context = ExecutionContext(flow_name, TEST_PRESET_TIMEPERIOD, TEST_START_TIMEPERIOD, TEST_END_TIMEPERIOD,
                                        settings.settings)
        self.cluster = EphemeralCluster('unit test cluster', self.context)

    def tearDown(self):
        pass

    def test_verbose_command(self):
        command = 'ls -al'
        if not path.curdir.endswith('tests'):
            command = 'cd tests; ' + command

        ls = self.cluster.run_shell_command(command)
        for f in ['test_ephemeral_cluster.py', 'test_flow_graph.py', 'ut_flows.py']:
            self.assertTrue(any(f in s for s in ls))

    def test_silent_command(self):
        ls = self.cluster.run_shell_command('mkdir -p /tmp/logs/synergy-flow/')
        self.assertIsNotNone(ls)

    def test_non_existent_command(self):
        try:
            self.cluster.run_shell_command('tratata -p /tmp/logs/synergy-flow/')
            self.assertTrue(False, 'exception should have been thrown since command *tratata* is unknown')
        except subprocess.CalledProcessError as e:
            self.assertTrue(True, 'expected exception, as command *tratata* is unknown')


if __name__ == '__main__':
    unittest.main()
