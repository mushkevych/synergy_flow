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
from flow.core.ephemeral_cluster import EphemeralFilesystem

TEST_PRESET_TIMEPERIOD = '2016060107'
TEST_START_TIMEPERIOD = '2016060107'
TEST_END_TIMEPERIOD = '2016060108'


class EphemeralFilesystemTest(unittest.TestCase):
    def setUp(self):
        flow_name = 'ut_flow_name'
        self.context = ExecutionContext(flow_name, TEST_PRESET_TIMEPERIOD, TEST_START_TIMEPERIOD, TEST_END_TIMEPERIOD,
                                        settings.settings)
        self.ephemeral_filesystem = EphemeralFilesystem('unit test cluster', self.context)

    def tearDown(self):
        pass

    def test_mkdir(self, uri_path, **kwargs):
        pass

    def test_rmdir(self, uri_path, **kwargs):
        pass

    def test_rm(self, uri_path, **kwargs):
        pass

    def test_cp(self, uri_source, uri_target, **kwargs):
        pass

    def test_mv(self, uri_source, uri_target, **kwargs):
        pass

    def test_copyToLocal(self, uri_source, uri_target, **kwargs):
        pass

    def test_copyFromLocal(self, uri_source, uri_target, **kwargs):
        pass


if __name__ == '__main__':
    unittest.main()
