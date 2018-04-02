__author__ = 'Bohdan Mushkevych'

import time

import boto3

from flow.core.abstract_cluster import AbstractCluster, ClusterError
from flow.core.s3_filesystem import S3Filesystem

# `http://boto3.readthedocs.io/en/latest/reference/services/emr.html#EMR.Client.describe_cluster`_
CLUSTER_STATE_TERMINATED_WITH_ERRORS = 'TERMINATED_WITH_ERRORS'
CLUSTER_STATE_TERMINATED = 'TERMINATED'
CLUSTER_STATE_TERMINATING = 'TERMINATING'
CLUSTER_STATE_WAITING = 'WAITING'
CLUSTER_STATE_RUNNING = 'RUNNING'
CLUSTER_STATE_BOOTSTRAPPING = 'BOOTSTRAPPING'
CLUSTER_STATE_STARTING = 'STARTING'

# `http://boto3.readthedocs.io/en/latest/reference/services/emr.html#EMR.Client.describe_step`_
STEP_STATE_PENDING = 'PENDING'
STEP_STATE_CANCEL_PENDING = 'CANCEL_PENDING'
STEP_STATE_RUNNING = 'RUNNING'
STEP_STATE_COMPLETED = 'COMPLETED'
STEP_STATE_CANCELLED = 'CANCELLED'
STEP_STATE_FAILED = 'FAILED'
STEP_STATE_INTERRUPTED = 'INTERRUPTED'


class EmrCluster(AbstractCluster):
    """ implementation of the abstract API for the case of AWS EMR """

    def __init__(self, name, context, **kwargs):
        super(EmrCluster, self).__init__(name, context, **kwargs)
        self._filesystem = S3Filesystem(self.logger, context, **kwargs)

        self.jobflow_id = None  # it is both ClusterId and the JobflowId

        self.client_b3 = boto3.client(service_name='emr',
                                      region_name=context.settings['aws_cluster_region'],
                                      aws_access_key_id=context.settings['aws_access_key_id'],
                                      aws_secret_access_key=context.settings['aws_secret_access_key'])

    @property
    def filesystem(self):
        return self._filesystem

    def _poll_step(self, step_id):
        """ method polls the state for given step_id and awaits its completion """

        def _current_state():
            step = self.client_b3.describe_step(ClusterId=self.jobflow_id, StepId=step_id)
            return step['Step']['Status']['State']

        state = _current_state()
        while state in [STEP_STATE_PENDING, STEP_STATE_RUNNING]:
            # Job flow step is being spawned. Idle and recheck the status.
            time.sleep(20.0)
            state = _current_state()

        if state in [STEP_STATE_CANCELLED, STEP_STATE_INTERRUPTED, STEP_STATE_CANCEL_PENDING, STEP_STATE_FAILED]:
            raise ClusterError('EMR Step {0} failed'.format(step_id))
        elif state == STEP_STATE_COMPLETED:
            self.logger.info('EMR Step {0} has completed'.format(step_id))
        else:
            self.logger.warning('Unknown state {0} during EMR Step {1} execution'.format(state, step_id))

        return state

    def run_pig_step(self, uri_script, **kwargs):
        """
        method starts a Pig step on a cluster and monitors its execution
        :raise EmrLauncherError: in case the cluster is not launched
        :return: step state or None if the step failed
        """

        # `https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-commandrunner.html`_
        # `http://boto3.readthedocs.io/en/latest/reference/services/emr.html#EMR.Client.add_job_flow_steps`_
        if not self.jobflow_id:
            raise ClusterError('EMR Cluster {0} is not launched'.format(self.name))

        self.logger.info('Pig Script Step {')
        try:
            step = {
                'Name': 'SynergyPigStep',
                'ActionOnFailure': 'CONTINUE',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': ['pig-script', '--run-pig-script', '--args', '-f', uri_script]
                }
            }
            if kwargs:
                properties = [{'Key': '{}'.format(k), 'Value': '{}'.format(v)} for k, v in kwargs.items()]
                step['HadoopJarStep']['Properties'] = properties

                step_args = []
                for k, v in kwargs.items():
                    step_args.append('-p')
                    step_args.append('{0}={1}'.format(k, v))
                step['HadoopJarStep']['Args'].extend(step_args)

            step_response = self.client_b3.add_job_flow_steps(JobFlowId=self.jobflow_id, Steps=[step])
            step_ids = step_response['StepIds']

            assert len(step_ids) == 1
            return self._poll_step(step_ids[0])
        except ClusterError as e:
            self.logger.error('Pig Script Step Error: {0}'.format(e), exc_info=True)
            return None
        except Exception as e:
            self.logger.error('Pig Script Step Unexpected Exception: {0}'.format(e), exc_info=True)
            return None
        finally:
            self.logger.info('}')

    def run_spark_step(self, uri_script, language, **kwargs):
        # `https://github.com/dev-86/aws-cli/blob/29756ea294aebc7c854b3d9a2b1a56df28637e11/tests/unit/customizations/emr/test_create_cluster_release_label.py`_
        # `https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-commandrunner.html`_
        # `http://boto3.readthedocs.io/en/latest/reference/services/emr.html#EMR.Client.add_job_flow_steps`_
        if not self.jobflow_id:
            raise ClusterError('EMR Cluster {0} is not launched'.format(self.name))

        self.logger.info('Spark Step {')
        try:
            step = {
                'Name': 'SynergyPysparkStep',
                'ActionOnFailure': 'CONTINUE',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': ['spark-submit', '--deploy-mode', 'cluster', uri_script]
                }
            }
            if kwargs:
                properties = [{'Key': '{}'.format(k), 'Value': '{}'.format(v)} for k, v in kwargs.items()]
                step['HadoopJarStep']['Properties'] = properties

            step_response = self.client_b3.add_job_flow_steps(JobFlowId=self.jobflow_id, Steps=[step])
            step_ids = step_response['StepIds']

            assert len(step_ids) == 1
            return self._poll_step(step_ids[0])
        except ClusterError as e:
            self.logger.error('Spark Step Error: {0}'.format(e), exc_info=True)
            return None
        except Exception as e:
            self.logger.error('Spark Step Unexpected Exception: {0}'.format(e), exc_info=True)
            return None
        finally:
            self.logger.info('}')

    def run_hadoop_step(self, uri_script, **kwargs):
        # `https://github.com/dev-86/aws-cli/blob/29756ea294aebc7c854b3d9a2b1a56df28637e11/tests/unit/customizations/emr/test_create_cluster_release_label.py`_
        pass

    def run_shell_command(self, uri_script, **kwargs):
        # `https://github.com/dev-86/aws-cli/blob/29756ea294aebc7c854b3d9a2b1a56df28637e11/tests/unit/customizations/emr/test_create_cluster_release_label.py`_
        pass

    def _launch(self):
        """
        method launches the cluster and returns when the cluster is fully operational
        and ready to accept business steps
        :see: `http://boto3.readthedocs.io/en/latest/reference/services/emr.html#EMR.Client.add_job_flow_steps`_
        """
        self.logger.info('Launching EMR Cluster {0} {{'.format(self.name))
        try:
            response = self.client_b3.run_job_flow(
                Name=self.context.settings['aws_cluster_name'],
                ReleaseLabel='emr-5.12.0',
                Instances={
                    'MasterInstanceType': 'm3.xlarge',
                    'SlaveInstanceType': 'm3.xlarge',
                    'InstanceCount': 3,
                    'KeepJobFlowAliveWhenNoSteps': True,
                    'TerminationProtected': True,
                    'Ec2KeyName': self.context.settings.get('aws_key_name', ''),
                },
                BootstrapActions=[
                    {
                        'Name': 'Maximize Spark Default Config',
                        'ScriptBootstrapAction': {
                            'Path': 's3://support.elasticmapreduce/spark/maximize-spark-default-config',
                        }
                    },
                ],
                Applications=[
                    {
                        'Name': 'Spark',
                    },
                    {
                        'Name': 'Pig',
                    },
                ],
                VisibleToAllUsers=True,
                JobFlowRole='EMR_EC2_DefaultRole',
                ServiceRole='EMR_DefaultRole'
            )

            self.logger.info('EMR Cluster Initialization Request Successful.')
            return response['JobFlowId']
        except:
            self.logger.error('EMR Cluster failed to launch', exc_info=True)
            raise ClusterError('EMR Cluster {0} launch failed'.format(self.name))
        finally:
            self.logger.info('}')

    def _get_cluster(self):
        try:
            clusters = self.client_b3.list_clusters(ClusterStates=['STARTING', 'BOOTSTRAPPING', 'RUNNING', 'WAITING'])
            for cluster in clusters['Clusters']:
                if cluster['Name'] != self.context.settings['aws_cluster_name']:
                    continue
                return cluster['Id']
            return None
        except:
            return None

    def _wait_for_cluster(self, cluster_id):
        """ method polls the state for the cluster and awaits until it is ready to start processing """

        def _current_state():
            cluster = self.client_b3.describe_cluster(ClusterId=cluster_id)
            return cluster['Cluster']['Status']['State']

        state = _current_state()
        while state in [CLUSTER_STATE_STARTING, CLUSTER_STATE_BOOTSTRAPPING, CLUSTER_STATE_RUNNING]:
            # Cluster is being spawned. Idle and recheck the status.
            time.sleep(20.0)
            state = _current_state()

        if state in [CLUSTER_STATE_TERMINATING, CLUSTER_STATE_TERMINATED, CLUSTER_STATE_TERMINATED_WITH_ERRORS]:
            raise ClusterError('EMR Cluster {0} launch failed'.format(self.name))
        elif state == CLUSTER_STATE_WAITING:
            # state WAITING marks readiness to process business steps
            cluster = self.client_b3.describe_cluster(ClusterId=cluster_id)
            master_dns = cluster['Cluster']['MasterPublicDnsName']
            self.logger.info('EMR Cluster Launched Successfully. Master DNS node is {0}'.format(master_dns))
        else:
            self.logger.warning('Unknown state {0} during EMR Cluster launch'.format(state))

        return state

    def launch(self):
        self.logger.info('Launching EMR Cluster: {0} {{'.format(self.context.settings['aws_cluster_name']))

        if self.jobflow_id \
                and self._wait_for_cluster(self.jobflow_id) in [CLUSTER_STATE_STARTING, CLUSTER_STATE_BOOTSTRAPPING,
                                                                CLUSTER_STATE_RUNNING]:
            raise ClusterError('EMR Cluster {0} has already been launched with id {1}. Use it or dispose it.'
                               .format(self.name, self.jobflow_id))

        cluster_id = self._get_cluster()
        if cluster_id:
            self.logger.info('Reusing existing EMR Cluster: {0} {{'.format(cluster_id))
        else:
            cluster_id = self._launch()
        self._wait_for_cluster(cluster_id)
        self.jobflow_id = cluster_id

        self.logger.info('}')

    def terminate(self):
        """ method terminates the cluster """
        if not self.jobflow_id:
            self.logger.info('No EMR Cluster to stop')
            return

        self.logger.info('Terminating EMR Cluster {')
        try:
            self.logger.info('Initiating termination procedure...')
            # Disable cluster termination protection
            self.client_b3.set_termination_protection(JobFlowIds=[self.jobflow_id], TerminationProtected=False)

            self.client_b3.terminate_job_flows(JobFlowIds=[self.jobflow_id])
            self.jobflow_id = None
            self.logger.info('Termination request successful')
        except Exception as e:
            self.logger.error('Unexpected Exception: {0}'.format(e), exc_info=True)
        finally:
            self.logger.info('}')
