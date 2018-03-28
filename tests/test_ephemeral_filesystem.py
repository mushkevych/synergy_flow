__author__ = 'Bohdan Mushkevych'

import random
import tempfile
import unittest

from os import path
from synergy.conf import settings
from flow.core.execution_context import ExecutionContext
from flow.core.ephemeral_cluster import EphemeralFilesystem

TEST_PRESET_TIMEPERIOD = '2016060107'
TEST_START_TIMEPERIOD = '2016060107'
TEST_END_TIMEPERIOD = '2016060108'
TEST_ROOT_NAME = 'unit-test-root'
TEST_FOLDER_NAME = 'temp-dir'
TEST_FOLDER_DEST = 'temp-dir-target'
TEMP_FILE_NAME = 'file_name_{0}.temporary'

CONTENT_STR = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz1234567890') for _ in range(1024)])
TEMP_CONTENT = CONTENT_STR.encode()


class EphemeralFilesystemTest(unittest.TestCase):
    def setUp(self):
        flow_name = 'ut_flow_name'
        self.context = ExecutionContext(flow_name, TEST_PRESET_TIMEPERIOD, TEST_START_TIMEPERIOD, TEST_END_TIMEPERIOD,
                                        settings.settings)
        self.filesystem = EphemeralFilesystem('unit test cluster', self.context)

    def tearDown(self):
        if self.filesystem.exists(TEST_ROOT_NAME):
            self.filesystem.rmdir(TEST_ROOT_NAME)

    def test_dir_basics(self):
        uri_path = path.join(TEST_ROOT_NAME, TEST_FOLDER_NAME)
        self.assertFalse(self.filesystem.exists(uri_path))
        self.filesystem.mkdir(uri_path)
        self.assertTrue(self.filesystem.exists(uri_path))
        self.filesystem.rmdir(uri_path)
        self.assertFalse(self.filesystem.exists(uri_path))

    def _upload_files(self, uri_source):
        list_uploaded_uri = list()
        for i in range(10):
            with tempfile.NamedTemporaryFile() as temp_file:
                temp_file.write(TEMP_CONTENT)
                temp_file.flush()

                upload_file_uri = path.join(uri_source, TEMP_FILE_NAME.format(i))
                list_uploaded_uri.append(upload_file_uri)

                self.filesystem.copyFromLocal(temp_file.name, upload_file_uri)
                self.assertTrue(self.filesystem.exists(upload_file_uri))
        return list_uploaded_uri

    def test_dir_with_files(self):
        uri_path = path.join(TEST_ROOT_NAME, TEST_FOLDER_NAME)
        self.filesystem.mkdir(uri_path)

        for i in range(10):
            with tempfile.NamedTemporaryFile() as temp_file:
                temp_file.write(TEMP_CONTENT)
                upload_file_uri = path.join(uri_path, TEMP_FILE_NAME.format(i))
                self.filesystem.copyFromLocal(temp_file.name, upload_file_uri)
                self.assertTrue(self.filesystem.exists(upload_file_uri))

    def test_cp_dir(self):
        uri_source = path.join(TEST_ROOT_NAME, TEST_FOLDER_NAME)
        uri_target = path.join(TEST_ROOT_NAME, TEST_FOLDER_DEST)
        self.filesystem.mkdir(uri_source)
        self._upload_files(uri_source)

        self.filesystem.cp(uri_source, uri_target)
        for i in range(10):
            temp_file_uri = path.join(uri_target, TEMP_FILE_NAME.format(i))
            self.assertTrue(self.filesystem.exists(temp_file_uri))

    def test_cp_file(self):
        uri_source_dir = path.join(TEST_ROOT_NAME, TEST_FOLDER_NAME)
        uri_target_dir = path.join(TEST_ROOT_NAME, TEST_FOLDER_DEST)
        self.filesystem.mkdir(uri_source_dir)
        self.filesystem.mkdir(uri_target_dir)
        list_uploaded_uri = self._upload_files(uri_source_dir)

        for uploaded_uri in list_uploaded_uri:
            uri_target = path.join(TEST_ROOT_NAME, TEST_FOLDER_DEST, path.basename(uploaded_uri))
            self.filesystem.cp(uploaded_uri, uri_target)
            self.assertTrue(self.filesystem.exists(uri_target))

    def test_mv(self):
        uri_source = path.join(TEST_ROOT_NAME, TEST_FOLDER_NAME)
        uri_target = path.join(TEST_ROOT_NAME, TEST_FOLDER_DEST)
        self.filesystem.mkdir(uri_source)
        list_uploaded_uri = self._upload_files(uri_source)

        self.filesystem.mv(uri_source, uri_target)
        for uploaded_uri in list_uploaded_uri:
            uri_target = path.join(TEST_ROOT_NAME, TEST_FOLDER_DEST, path.basename(uploaded_uri))
            self.assertTrue(self.filesystem.exists(uri_target))

    def test_copyToLocal(self):
        uri_path = path.join(TEST_ROOT_NAME, TEST_FOLDER_NAME)
        self.filesystem.mkdir(uri_path)
        list_uploaded_uri = self._upload_files(uri_path)

        for uploaded_uri in list_uploaded_uri:
            downloaded_uri = path.join(tempfile.gettempdir(), path.basename(uploaded_uri))
            self.filesystem.copyToLocal(uploaded_uri, downloaded_uri)
            self.assertTrue(path.exists(downloaded_uri))

            with open(downloaded_uri) as downloaded_file:
                self.assertEqual(downloaded_file.read().encode(), TEMP_CONTENT)


if __name__ == '__main__':
    unittest.main()
