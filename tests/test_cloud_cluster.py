__author__ = 'Bohdan Mushkevych'

import unittest
from synergy.conf import settings
from flow.core.execution_context import ExecutionContext
from flow.core.abstract_cluster import ClusterError
from flow.core.gcp_cluster import GcpCluster, JOB_STATE_DONE
from flow.core.emr_cluster import EmrCluster, STEP_STATE_COMPLETED

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
        # pass

    @unittest.skip('simply skip')
    def test_non_running_cluster(self):
        try:
            self.cluster.run_spark_step('code/pyspark_sort.py', 'pyspark')
            self.assertTrue(False, 'Cluster not started expected exception not raised')
        except ClusterError as e:
            self.assertTrue(True, 'Cluster not started exception caught')

    @unittest.skip('skip basics')
    def test_cluster_basics(self):
        self.cluster.launch()
        self.assertIsNotNone(self.cluster.cluster_details)

        result = self.cluster._get_cluster()
        self.assertIsNotNone(result)

        self.cluster.terminate()
        self.assertIsNone(self.cluster.cluster_details)

    @unittest.skip('skip spark step')
    def test_spark_job(self):
        self.cluster.filesystem.copyFromLocal('pyspark_sort.py', 'code/pyspark_sort.py')
        self.cluster.launch()
        state = self.cluster.run_spark_step('code/pyspark_sort.py', 'python')
        self.assertEqual(state, JOB_STATE_DONE)

    @unittest.skip('skip pig step')
    def test_pig_job(self):
        self.cluster.filesystem.copyFromLocal('pig_sample.pig', 'code/pig_sample.pig')
        self.cluster.filesystem.copyFromLocal('drivers.csv', 'code/drivers.csv')
        self.cluster.filesystem.copyFromLocal('truck_event_text_partition.csv', 'code/truck_event_text_partition.csv')
        self.cluster.launch()

        data_trucks = 'gs://{}/{}'.format(self.context.settings['gcp_bucket'], 'code/truck_event_text_partition.csv')
        data_drivers = 'gs://{}/{}'.format(self.context.settings['gcp_bucket'], 'code/drivers.csv')
        state = self.cluster.run_pig_step('code/pig_sample.pig', TRUCKS_CSV=data_trucks, DRIVERS_CSV=data_drivers)
        self.assertEqual(state, JOB_STATE_DONE)


@unittest.skip('Automated testing will fail due to lack of credentials')
class EmrClusterTest(unittest.TestCase):
    def setUp(self):
        flow_name = 'ut_flow_name'
        self.context = ExecutionContext(flow_name, TEST_PRESET_TIMEPERIOD, TEST_START_TIMEPERIOD, TEST_END_TIMEPERIOD,
                                        settings.settings)
        self.cluster = EmrCluster('unit test cluster', self.context)

    def tearDown(self):
        # self.cluster.terminate()
        pass

    @unittest.skip('simply skip')
    def test_non_running_cluster(self):
        try:
            self.cluster.run_spark_step('code/pyspark_sort.py', 'pyspark')
            self.assertTrue(False, 'Cluster not started expected exception not raised')
        except ClusterError as e:
            self.assertTrue(True, 'Cluster not started exception caught')

    # @unittest.skip('skip basics')
    def test_cluster_basics(self):
        self.cluster.launch()
        self.assertIsNotNone(self.cluster.jobflow_id)

        self.cluster.terminate()
        self.assertIsNone(self.cluster.jobflow_id)

    @unittest.skip('skip spark step')
    def test_spark_job(self):
        self.cluster.filesystem.copyFromLocal('pyspark_sort.py', 'code/pyspark_sort.py')
        self.cluster.launch()
        state = self.cluster.run_spark_step('code/pyspark_sort.py', 'python')
        self.assertEqual(state, STEP_STATE_COMPLETED)

    @unittest.skip('skip pig step')
    def test_pig_job(self):
        self.cluster.filesystem.copyFromLocal('pig_sample.pig', 'code/pig_sample.pig')
        self.cluster.filesystem.copyFromLocal('drivers.csv', 'code/drivers.csv')
        self.cluster.filesystem.copyFromLocal('truck_event_text_partition.csv', 'code/truck_event_text_partition.csv')
        self.cluster.launch()

        data_trucks = 's3a://{}/{}'.format(self.context.settings['gcp_bucket'], 'code/truck_event_text_partition.csv')
        data_drivers = 's3a://{}/{}'.format(self.context.settings['gcp_bucket'], 'code/drivers.csv')
        state = self.cluster.run_pig_step('code/pig_sample.pig', TRUCKS_CSV=data_trucks, DRIVERS_CSV=data_drivers)
        self.assertEqual(state, STEP_STATE_COMPLETED)


if __name__ == '__main__':
    unittest.main()
