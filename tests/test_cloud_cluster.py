__author__ = 'Bohdan Mushkevych'

import unittest
from synergy.conf import settings
from flow.core.execution_context import ExecutionContext
from flow.core.abstract_cluster import ClusterError
from flow.core.gcp_cluster import GcpCluster, JOB_STATE_DONE, JOB_STATE_ERROR

TEST_PRESET_TIMEPERIOD = '2016060107'
TEST_START_TIMEPERIOD = '2016060107'
TEST_END_TIMEPERIOD = '2016060108'


@unittest.skip('Automated testing will fail due to lack of credentials')
class GcpClusterTest(unittest.TestCase):
    def setUp(self):
        flow_name = 'ut_flow_name'
        self.context = ExecutionContext(flow_name, TEST_PRESET_TIMEPERIOD, TEST_START_TIMEPERIOD, TEST_END_TIMEPERIOD,
                                        settings.settings)
        self.cluster = GcpCluster('unit test cluster', self.context)

    def tearDown(self):
        self.cluster.terminate()

    # @unittest.skip('temporary')
    def test_non_running_cluster(self):
        try:
            self.cluster.run_spark_step('code/pyspark_sort.py', 'pyspark')
            self.assertTrue(False, 'Cluster not started expected exception not raised')
        except ClusterError as e:
            self.assertTrue(True, 'Cluster not started exception caught')

    def test_cluster_basics(self):
        self.cluster.launch()
        self.assertIsNotNone(self.cluster.cluster_details)

        result = self.cluster._get_cluster()
        self.assertIsNotNone(result)

        self.cluster.terminate()
        self.assertIsNone(self.cluster.cluster_details)

    def test_spark_job(self):
        self.cluster.filesystem.copyFromLocal('pyspark_sort.py', 'code/pyspark_sort.py')
        self.cluster.launch()
        state, details = self.cluster.run_spark_step('code/pyspark_sort.py', 'python')
        self.assertIn(state, [JOB_STATE_DONE, JOB_STATE_ERROR])
        self.assertNotEqual(details, 'NA')
        # ['Hello,', 'dog', 'elephant', 'panther', 'world!']


if __name__ == '__main__':
    unittest.main()
