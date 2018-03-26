__author__ = 'Bohdan Mushkevych'

import unittest

from synergy.conf import settings
from flow.core.execution_context import ExecutionContext
from flow.core.gcp_filesystem import GcpFilesystem
from flow.core.azure_blob_filesystem import AzureBlobFilesystem
from flow.core.s3_filesystem import S3Filesystem
from tests.test_ephemeral_filesystem import EphemeralFilesystemTest

TEST_PRESET_TIMEPERIOD = '2016060107'
TEST_START_TIMEPERIOD = '2016060107'
TEST_END_TIMEPERIOD = '2016060108'


@unittest.skip('Automated testing will fail due to lack of credentials')
class GcpFilesystemTest(EphemeralFilesystemTest):
    def setUp(self):
        flow_name = 'ut_flow_name'
        self.context = ExecutionContext(flow_name, TEST_PRESET_TIMEPERIOD, TEST_START_TIMEPERIOD, TEST_END_TIMEPERIOD,
                                        settings.settings)
        self.filesystem = GcpFilesystem('unit test cluster', self.context)


@unittest.skip('Automated testing will fail due to lack of credentials')
class S3FilesystemTest(EphemeralFilesystemTest):
    def setUp(self):
        flow_name = 'ut_flow_name'
        self.context = ExecutionContext(flow_name, TEST_PRESET_TIMEPERIOD, TEST_START_TIMEPERIOD, TEST_END_TIMEPERIOD,
                                        settings.settings)
        self.filesystem = S3Filesystem('unit test cluster', self.context)


@unittest.skip('Automated testing will fail due to lack of credentials')
class AzureFilesystemTest(EphemeralFilesystemTest):
    def setUp(self):
        flow_name = 'ut_flow_name'
        self.context = ExecutionContext(flow_name, TEST_PRESET_TIMEPERIOD, TEST_START_TIMEPERIOD, TEST_END_TIMEPERIOD,
                                        settings.settings)
        self.filesystem = AzureBlobFilesystem('unit test cluster', self.context)


if __name__ == '__main__':
    unittest.main()
