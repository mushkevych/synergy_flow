__author__ = 'Bohdan Mushkevych'

import time

import boto.emr
from boto.emr.bootstrap_action import BootstrapAction
from boto.emr.emrobject import ClusterStatus, StepId, JobFlow, JobFlowStepList
from boto.emr.step import InstallPigStep
from boto.emr.step import PigStep

from flow.core.abstract_cluster import AbstractCluster, ClusterError

# `http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/ProcessingCycle.html`_
CLUSTER_STATE_COMPLETED = 'COMPLETED'
CLUSTER_STATE_TERMINATED = 'TERMINATED'
CLUSTER_STATE_FAILED = 'FAILED'
CLUSTER_STATE_SHUTTING_DOWN = 'SHUTTING_DOWN'
CLUSTER_STATE_WAITING = 'WAITING'
CLUSTER_STATE_RUNNING = 'RUNNING'
CLUSTER_STATE_BOOTSTRAPPING = 'BOOTSTRAPPING'
CLUSTER_STATE_STARTING = 'STARTING'

# `http://docs.aws.amazon.com/ElasticMapReduce/latest/API/API_StepExecutionStatusDetail.html`_
STEP_STATE_PENDING = 'PENDING'
STEP_STATE_RUNNING = 'RUNNING'
STEP_STATE_CONTINUE = 'CONTINUE'
STEP_STATE_COMPLETED = 'COMPLETED'
STEP_STATE_CANCELLED = 'CANCELLED'
STEP_STATE_FAILED = 'FAILED'
STEP_STATE_INTERRUPTED = 'INTERRUPTED'


class EmrCluster(AbstractCluster):
    """ implementation of the abstract API for the case of AWS EMR """
    def __init__(self, name, context, **kwargs):
        super(EmrCluster, self).__init__(name, context, kwargs)

        self.jobflow_id = None  # it is both ClusterId and the JobflowId

        # Setting up boto.emr.connection.EmrConnection
        self.conn = boto.emr.connect_to_region(region_name=context.settings['aws_region'],
                                               aws_access_key_id=context.settings['aws_access_key_id'],
                                               aws_secret_access_key=context.settings['aws_secret_access_key'])

    def run_pig_step(self, uri_script, **kwargs):
        """
        method starts a Pig step on a cluster and monitors its execution
        :raise EmrLauncherError: in case the cluster is not launched
        :return: step state or None if the step failed
        """
        if not self.jobflow_id:
            raise ClusterError('EMR Cluster {0} is not launched'.format(self.name))

        if not kwargs: kwargs = {}

        self.logger.info('Pig Script Step {')
        try:
            self.logger.info('Initiating the step...')
            step_args = []
            for k, v in kwargs.items():
                step_args.append('-p')
                step_args.append('{0}={1}'.format(k, v))

            pig_runner_step = PigStep(name='SynergyPigStep', pig_file=uri_script, pig_args=step_args)
            step_list = self.conn.add_jobflow_steps(self.jobflow_id, pig_runner_step)

            self.logger.info('Step Initiated Successfully. Validating its state...')

            assert isinstance(step_list, JobFlowStepList)
            assert len(step_list.stepids) == 1

            step_id = step_list.stepids[0]
            assert isinstance(step_id, StepId)
            return self._poll_step(step_id.value)
        except ClusterError as e:
            self.logger.error('Pig Script Step Error: {0}'.format(e), exc_info=True)
            return None
        except Exception as e:
            self.logger.error('Pig Script Step Unexpected Exception: {0}'.format(e), exc_info=True)
            return None
        finally:
            self.logger.info('}')

    def run_spark_step(self, uri_script, **kwargs):
        pass

    def run_hadoop_step(self, uri_script, **kwargs):
        pass

    def run_shell_command(self, uri_script, **kwargs):
        pass

    def launch(self):
        """
        method launches the cluster and returns when the cluster is fully operational
        and ready to accept business steps
        :see: `http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/emr-plan-bootstrap.html/`_
        """
        if self.jobflow_id:
            raise ClusterError('EMR Cluster {0} has already been launched with id {1}. Use it or dispose it.'
                               .format(self.name, self.jobflow_id))

        self.logger.info('Launching EMR Cluster {0} {{'.format(self.name))
        try:
            hadoop_config_params = ['-h', 'dfs.block.size=134217728',
                                    '-h', 'dfs.datanode.max.transfer.threads=4096']
            hadoop_config_bootstrapper = BootstrapAction('hadoop-config',
                                                         's3://elasticmapreduce/bootstrap-actions/configure-hadoop',
                                                         hadoop_config_params)
            # Pig Installation
            pig_install_step = InstallPigStep()

            # Launching the cluster
            self.jobflow_id = self.conn.run_jobflow(
                name=self.name,
                enable_debugging=True,
                visible_to_all_users=True,
                log_uri=self.context.settings['emr_log_uri'] + '/' + self.name,
                bootstrap_actions=[hadoop_config_bootstrapper],
                ec2_keyname=self.context.settings['emr_keyname'],
                steps=[pig_install_step],
                keep_alive=True,
                action_on_failure='CANCEL_AND_WAIT',
                master_instance_type=self.context.settings['emr_master_type'],
                slave_instance_type=self.context.settings['emr_slave_type'],
                num_instances=self.context.settings['emr_num_instance'],
                ami_version=self.context.settings['emr_ami_version']
            )

            # Enable cluster termination protection
            self.conn.set_termination_protection(self.jobflow_id, True)
            self.logger.info('EMR Cluster Initialization Complete. Validating cluster state...')

            self._poll_cluster()
        except:
            self.logger.error('EMR Cluster failed to launch', exc_info=True)
            raise ClusterError('EMR Cluster {0} launch failed'.format(self.name))
        finally:
            self.logger.info('}')

    def _poll_cluster(self):
        """ method polls the state for the cluster and awaits until it is ready to start processing """

        def _current_state():
            jobflow = self.conn.describe_jobflow(self.jobflow_id)
            assert isinstance(jobflow, JobFlow)
            return jobflow.state

        state = _current_state()
        while state in [CLUSTER_STATE_STARTING, CLUSTER_STATE_BOOTSTRAPPING, CLUSTER_STATE_RUNNING]:
            # Cluster is being spawned. Idle and recheck the status.
            time.sleep(20.0)
            state = _current_state()

        if state in [CLUSTER_STATE_SHUTTING_DOWN, CLUSTER_STATE_TERMINATED,
                     CLUSTER_STATE_COMPLETED, CLUSTER_STATE_FAILED]:
            raise ClusterError('EMR Cluster {0} launch failed'.format(self.name))
        elif state == CLUSTER_STATE_WAITING:
            # state WAITING marks readiness to process business steps
            master_dns = self.conn.describe_jobflow(self.jobflow_id).masterpublicdnsname
            self.logger.info('EMR Cluster Launched Successfully. Master DNS node is {0}'.format(master_dns))
        else:
            self.logger.warning('Unknown state {0} during EMR Cluster launch'.format(state))

        return state

    def _poll_step(self, step_id):
        """ method polls the state for given step_id and awaits its completion """

        def _current_state():
            step_description = self.conn.describe_step(self.jobflow_id, step_id)
            step_status = step_description.status
            assert isinstance(step_status, ClusterStatus)
            return step_status.state

        state = _current_state()
        while state in [STEP_STATE_PENDING, STEP_STATE_RUNNING, STEP_STATE_CONTINUE]:
            # Job flow step is being spawned. Idle and recheck the status.
            time.sleep(20.0)
            state = _current_state()

        if state in [STEP_STATE_CANCELLED, STEP_STATE_INTERRUPTED, STEP_STATE_FAILED]:
            raise ClusterError('EMR Step {0} failed'.format(step_id))
        elif state == STEP_STATE_COMPLETED:
            self.logger.info('EMR Step {0} has completed'.format(step_id))
        else:
            self.logger.warning('Unknown state {0} during EMR Step {1} execution'.format(state, step_id))

        return state

    def terminate(self):
        """ method terminates the cluster """
        if not self.jobflow_id:
            self.logger.info('No EMR Cluster to stop')
            return

        self.logger.info('EMR Cluster termination {')
        try:
            self.logger.info('Initiating termination procedure...')
            # Disable cluster termination protection
            self.conn.set_termination_protection(self.jobflow_id, False)

            self.conn.terminate_jobflow(self.jobflow_id)
            self.logger.info('termination request send successfully')
        except Exception as e:
            self.logger.error('Unexpected Exception: {0}'.format(e), exc_info=True)
        finally:
            self.logger.info('}')
