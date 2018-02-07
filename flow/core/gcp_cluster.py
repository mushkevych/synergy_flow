__author__ = 'Bohdan Mushkevych'

import googleapiclient.discovery
from google.cloud import dataproc

from synergy.conf import settings
from flow.core.abstract_cluster import AbstractCluster
from flow.core.gcp_filesystem import GcpFilesystem


class GcpCluster(AbstractCluster):
    """ implementation of the Google Cloud Platform Dataproc API """

    def __init__(self, name, context, **kwargs):
        super(GcpCluster, self).__init__(name, context, kwargs=kwargs)
        self._filesystem = GcpFilesystem(self.logger, context, **kwargs)

        self.dataproc = googleapiclient.discovery.build('dataproc', 'v1')
        self.cluster = None
        self.project_id = context.settings['gcp_project_id']
        self.cluster_name = context.settings['gcp_cluster_name']
        self.cluster_region = context.settings['gcp_cluster_region']
        self.cluster_zone = context.settings['gcp_cluster_zone']

    @property
    def filesystem(self):
        return self._filesystem

    def _poll_step(self, job_id):
        print('Waiting for job to finish...')
        while True:
            result = self.dataproc.projects().regions().jobs().get(
                projectId=self.project_id,
                region=self.cluster_region,
                jobId=job_id).execute()

            # Handle exceptions
            if result['status']['state'] == 'ERROR':
                raise Exception(result['status']['details'])
            elif result['status']['state'] == 'DONE':
                print('Job finished.')
                return result

    def _run_step(self, job_details):
        result = self.dataproc.projects().regions().jobs().submit(
            projectId=self.project_id,
            region=self.cluster_region,
            body=job_details).execute()
        job_id = result['reference']['jobId']

        self.logger.info('Submitted job ID {0}. Waiting for completion'.format(job_id))
        return self._poll_step(job_id)

    def run_pig_step(self, uri_script, **kwargs):
        # `https://cloud.google.com/dataproc/docs/reference/rest/v1beta2/PigJob`
        job_details = {
            'projectId': self.project_id,
            'job': {
                'placement': {
                    'clusterName': self.cluster_name
                },
                'pigJob': {
                    'scriptVariables': {
                        **kwargs
                    },
                    'queryFileUri': 'gs://{}/{}'.format(self., filename),

                }
            }
        }
        self._run_step(job_details)

    def run_spark_step(self, uri_script, language, **kwargs):
        # `https://cloud.google.com/dataproc/docs/reference/rest/v1beta2/PySparkJob`
        job_details = {
            'projectId': self.project_id,
            'job': {
                'placement': {
                    'clusterName': self.cluster_name
                },
                'pigJob': {
                    'mainPythonFileUri': 'gs://{}/{}'.format(self., filename),
                    'pythonFileUris': 'gs://{}/{}'.format(self., filename),
                }
            }
        }
        self._run_step(job_details)

    def run_hadoop_step(self, uri_script, **kwargs):
        # `https://cloud.google.com/dataproc/docs/reference/rest/v1beta2/HadoopJob`
        job_details = {
            'projectId': self.project_id,
            'job': {
                'placement': {
                    'clusterName': self.cluster_name
                },
                'hadoopJob': {
                    'mainClass': 'gs://{}/{}'.format(bucket_name, filename),

                }
            }
        }
        self._run_step(job_details)

    def run_shell_command(self, uri_script, **kwargs):
        raise NotImplementedError('TODO: implement shell command')

    def launch(self):
        zone_uri = \
            'https://www.googleapis.com/compute/v1/projects/{}/zones/{}'.format(self.project_id, self.cluster_zone)
        self.logger.info('Launching cluster: {0}'.format(zone_uri))

        cluster_data = {
            'projectId': self.project_id,
            'clusterName': self.cluster_name,
            'config': {
                'gceClusterConfig': {
                    'zoneUri': zone_uri
                }
            }
        }
        cluster = self.dataproc.projects().regions().clusters().create(
            projectId=self.project_id,
            region=self.cluster_region,
            body=cluster_data).execute()
        self.cluster = cluster

    def terminate(self):
        result = self.dataproc.projects().regions().clusters().delete(
            projectId=self.project_id,
            region=self.cluster_region,
            clusterName=self.cluster_name).execute()
        return result
