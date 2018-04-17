__author__ = 'Bohdan Mushkevych'

import time
import googleapiclient.discovery

from flow.core.abstract_cluster import AbstractCluster, ClusterError
from flow.core.gcp_filesystem import GcpFilesystem
from flow.core.gcp_credentials import gcp_credentials

# `https://cloud.google.com/dataproc/docs/reference/rest/v1/projects.regions.clusters#ClusterStatus`_
CLUSTER_STATE_UNKNOWN = 'UNKNOWN'
CLUSTER_STATE_CREATING = 'CREATING'
CLUSTER_STATE_RUNNING = 'RUNNING'
CLUSTER_STATE_ERROR = 'ERROR'
CLUSTER_STATE_DELETING = 'DELETING'
CLUSTER_STATE_UPDATING = 'UPDATING'

OPERATION_STATE_PENDING = 'PENDING'
OPERATION_STATE_SETUP_DONE = 'SETUP_DONE'

# `https://cloud.google.com/dataproc/docs/concepts/jobs/life-of-a-job`_
JOB_STATE_PENDING = 'PENDING'
JOB_STATE_RUNNING = 'RUNNING'
JOB_STATE_QUEUED = 'QUEUED'
JOB_STATE_DONE = 'DONE'
JOB_STATE_ERROR = 'ERROR'


class GcpCluster(AbstractCluster):
    """ implementation of the Google Cloud Platform Dataproc API """

    def __init__(self, name, context, **kwargs):
        super(GcpCluster, self).__init__(name, context, kwargs=kwargs)
        self._filesystem = GcpFilesystem(self.logger, context, **kwargs)
        service_account_file_uri = self.context.settings.get('gcp_service_account_file')
        credentials = gcp_credentials(service_account_file_uri)
        self.dataproc = googleapiclient.discovery.build('dataproc', 'v1', credentials=credentials)

        self.cluster_details = None
        self.project_id = context.settings['gcp_project_id']
        self.cluster_name = context.settings['gcp_cluster_name']
        self.cluster_region = context.settings['gcp_cluster_region']
        self.cluster_zone = context.settings['gcp_cluster_zone']

    @property
    def filesystem(self):
        return self._filesystem

    def _run_step(self, job_details):
        if not self.cluster_details:
            raise ClusterError('EMR Cluster {0} is not launched'.format(self.cluster_name))

        result = self.dataproc.projects().regions().jobs().submit(
            projectId=self.project_id,
            region=self.cluster_region,
            body=job_details).execute()
        job_id = result['reference']['jobId']

        self.logger.info('Submitted job ID {0}. Waiting for completion'.format(job_id))
        return self._poll_step(job_id)

    def _poll_step(self, job_id):
        details = 'NA'
        state = JOB_STATE_PENDING
        while state in [OPERATION_STATE_SETUP_DONE, JOB_STATE_PENDING, JOB_STATE_RUNNING, JOB_STATE_QUEUED]:
            result = self.dataproc.projects().regions().jobs().get(
                projectId=self.project_id,
                region=self.cluster_region,
                jobId=job_id).execute()
            state = result['status']['state']
            if 'details' in result['status']:
                details = result['status']['details']

        if state == JOB_STATE_ERROR:
            raise ClusterError('Gcp Job {0} failed: {1}'.format(job_id, details))
        elif state == JOB_STATE_DONE:
            self.logger.info('Gcp Job {0} has completed.')
        else:
            self.logger.warning('Unknown state {0} during Gcp Job {1} execution'.format(state, job_id))
        return state

    def run_pig_step(self, uri_script, libs=None, **kwargs):
        # `https://cloud.google.com/dataproc/docs/reference/rest/v1beta2/PigJob`_

        job_details = {
            'projectId': self.project_id,
            'job': {
                'placement': {
                    'clusterName': self.cluster_name
                },
                'pigJob': {
                    'queryFileUri': 'gs://{}/{}'.format(self.context.settings['gcp_code_bucket'], uri_script)
                }
            }
        }

        if kwargs:
            job_details['job']['pigJob']['scriptVariables'] = '{}'.format(kwargs)
        if libs:
            gs_libs = ['gs://{}/{}'.format(self.context.settings['gcp_code_bucket'], x) for x in libs]
            job_details['job']['pigJob']['jarFileUris'] = '{}'.format(gs_libs)

        return self._run_step(job_details)

    def run_spark_step(self, uri_script, language, libs=None, **kwargs):
        # `https://cloud.google.com/dataproc/docs/reference/rest/v1beta2/PySparkJob`_
        job_details = {
            'projectId': self.project_id,
            'job': {
                'placement': {
                    'clusterName': self.cluster_name
                },
                'pysparkJob': {
                    'mainPythonFileUri': 'gs://{}/{}'.format(self.context.settings['gcp_code_bucket'], uri_script)
                }
            }
        }

        if libs:
            gs_libs = ['gs://{}/{}'.format(self.context.settings['gcp_code_bucket'], x) for x in libs]
            job_details['job']['pysparkJob']['pythonFileUris'] = '{}'.format(gs_libs)

        return self._run_step(job_details)

    def run_hadoop_step(self, uri_script, **kwargs):
        # `https://cloud.google.com/dataproc/docs/reference/rest/v1beta2/HadoopJob`_
        raise NotImplementedError('Implement run_hadoop_step for the Gcp cluster')

    def run_shell_command(self, uri_script, **kwargs):
        raise NotImplementedError('TODO: implement shell command')

    def _launch(self):
        zone_uri = \
            'https://www.googleapis.com/compute/v1/projects/{}/zones/{}'.format(self.project_id, self.cluster_zone)
        cluster_data = {
            'projectId': self.project_id,
            'clusterName': self.cluster_name,
            'config': {
                'gceClusterConfig': {
                    'zoneUri': zone_uri
                },
                'masterConfig': {
                    'numInstances': 1,
                    'machineTypeUri': 'n1-standard-1'
                },
                'workerConfig': {
                    'numInstances': 2,
                    'machineTypeUri': 'n1-standard-1'
                }
            }
        }
        result = self.dataproc.projects().regions().clusters().create(
            projectId=self.project_id,
            region=self.cluster_region,
            body=cluster_data).execute()

        if result['metadata']['status']['state'] in [CLUSTER_STATE_CREATING, CLUSTER_STATE_RUNNING,
                                                     CLUSTER_STATE_UPDATING, OPERATION_STATE_PENDING]:
            self.logger.info('Launch request successful')
        else:
            self.logger.warning('Cluster {0} entered unknown state {1}'.
                                format(self.cluster_name, result['metadata']['status']['state']))

    def _get_cluster(self):
        try:
            result = self.dataproc.projects().regions().clusters().get(
                projectId=self.project_id,
                region=self.cluster_region,
                clusterName=self.cluster_name).execute()
            return result
        except:
            return None

    def _wait_for_cluster(self):
        cluster = self._get_cluster()
        while cluster:
            if cluster['status']['state'] == CLUSTER_STATE_ERROR:
                raise ClusterError('Cluster {0} creation error: {1}'.
                                   format(self.cluster_name, cluster['status']['details']))
            if cluster['status']['state'] == CLUSTER_STATE_RUNNING:
                self.logger.info('Cluster {0} is running'.format(self.cluster_name))
                break
            else:
                time.sleep(5)
                cluster = self._get_cluster()
        return cluster

    def launch(self):
        self.logger.info('Launching Gcp Cluster: {0} {{'.format(self.cluster_name))

        if not self._get_cluster():
            self._launch()
        self.cluster_details = self._wait_for_cluster()

        self.logger.info('}')

    def terminate(self):
        self.logger.info('Terminating Gcp Cluster {')
        result = self.dataproc.projects().regions().clusters().delete(
            projectId=self.project_id,
            region=self.cluster_region,
            clusterName=self.cluster_name).execute()

        if result['metadata']['status']['state'] in [CLUSTER_STATE_DELETING, CLUSTER_STATE_UNKNOWN,
                                                     OPERATION_STATE_PENDING]:
            self.cluster_details = None
            self.logger.info('Termination request successful')
        else:
            self.logger.warning('Cluster {0} entered unknown state {1}'.
                                format(self.cluster_name, result['metadata']['status']['state']))
        self.logger.info('}')
