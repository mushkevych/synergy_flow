__author__ = 'Bohdan Mushkevych'

import random
import unittest

from synergy.conf import settings
from flow.core.execution_context import ExecutionContext
from core.gcp_filesystem import GcpFilesystem
from test_ephemeral_filesystem import EphemeralFilesystemTest

TEST_PRESET_TIMEPERIOD = '2016060107'
TEST_START_TIMEPERIOD = '2016060107'
TEST_END_TIMEPERIOD = '2016060108'
TEST_ROOT_NAME = 'unit-test-root'
TEST_FOLDER_NAME = 'temp-dir'
TEST_FOLDER_DEST = 'temp-dir-target'
TEMP_FILE_NAME = 'file_name_{0}.temporary'

CONTENT_STR = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz1234567890') for _ in range(1024)])
TEMP_CONTENT = CONTENT_STR.encode()


@unittest.skip('Automated testing will fail due to lack of credentials')
class GcpFilesystemTest(EphemeralFilesystemTest):
    def setUp(self):
        flow_name = 'ut_flow_name'
        settings.settings['gcp_service_account_file'] = '../CloudProto-6a433c176b31.json'
        settings.settings['gcp_project_name'] = 'CloudProto'
        settings.settings['gcp_bucket'] = 'bucket-connect-proto'
        self.context = ExecutionContext(flow_name, TEST_PRESET_TIMEPERIOD, TEST_START_TIMEPERIOD, TEST_END_TIMEPERIOD,
                                        settings.settings)
        self.filesystem = GcpFilesystem('unit test cluster', self.context)


if __name__ == '__main__':
    unittest.main()
