__author__ = 'Bohdan Mushkevych'

import copy
from concurrent.futures import ThreadPoolExecutor, as_completed

from flow.conf import flows
from flow.core.abstract_cluster import AbstractCluster
from flow.core.emr_cluster import EmrCluster
from flow.core.flow_graph import FlowGraph
from flow.core.execution_context import ExecutionContext
from flow.core.ephemeral_cluster import EphemeralCluster


def launch_cluster(logger, context, cluster_name):
    if context.settings['cluster_type'] == 'emr':
        cluster = EmrCluster(logger, cluster_name)
    else:
        cluster = EphemeralCluster(logger, cluster_name)

    cluster.launch()
    return cluster


def parallel_flow_execution(logger, context, execution_cluster, flow_graph_obj):
    """ function fetches next available GraphNode/Step
        from the FlowGraph and executes it on the given cluster """
    assert isinstance(context, ExecutionContext)
    assert isinstance(execution_cluster, AbstractCluster)
    assert isinstance(flow_graph_obj, FlowGraph)
    for step_name in flow_graph_obj:
        try:
            graph_node = flow_graph_obj[step_name]
            graph_node.set_context(context)
            graph_node.run(execution_cluster)
        except Exception:
            logger.error('Exception during Step {0}'.format(step_name), exc_info=True)
            raise


class ExecutionEngine(object):
    """ Engine that triggers and supervises execution of the flow:
        - spawning multiple Execution Clusters (such as AWS EMR)
        - assigns execution steps to the clusters and monitor their progress
        - tracks dependencies and terminate execution should the Flow Critical Path fail """

    def __init__(self, logger, flow_name):
        assert isinstance(flow_name, FlowGraph)
        self.logger = logger
        if flow_name not in flows:
            raise ValueError('flow {0} not registered among flows: {1}'.format(flow_name, flows))

        self.flow_graph_obj = copy.deepcopy(flows[flow_name])

        # list of execution clusters (such as AWS EMR) available for processing
        self.execution_clusters = list()

    def _spawn_clusters(self, context):
        self.logger.info('spawning clusters...')
        with ThreadPoolExecutor(max_workers=context.number_of_clusters) as executor:
            future_to_cluster = [executor.submit(launch_cluster, self.logger, context,
                                                 'EmrComputingCluster-{0}'.format(i))
                                 for i in range(context.number_of_clusters)]
            for future in as_completed(future_to_cluster):
                try:
                    cluster = future.result()
                    self.execution_clusters.append(cluster)
                except Exception as exc:
                    self.logger.error('Cluster launch generated an exception: {0}'.format(exc))

    def _run_engine(self, context):
        self.logger.info('starting engine...')
        with ThreadPoolExecutor(max_workers=len(self.execution_clusters)) as executor:

            # Start the GraphNode/Step as soon as the step is unblocked and available for run
            # each future is marked with the execution_cluster
            future_to_worker = {executor.submit(parallel_flow_execution, self.logger,
                                                context, cluster, self.flow_graph_obj): cluster
                                for cluster in self.execution_clusters}

            for future in as_completed(future_to_worker):
                cluster = future_to_worker[future]
                try:
                    is_step_complete = future.result()
                    if not is_step_complete:
                        self.logger.error('Execution failed at cluster {0}'.format(cluster))
                except Exception as exc:
                    self.logger.error('Execution generated an exception at worker {0}: {1}'
                                      .format(cluster, exc))

    def run(self, context):
        """ method executes the flow by:
            - spawning clusters
            - traversing the FlowGraph and assigning
              steps for concurrent execution (if permitted by the Graph layout)
            - terminating clusters after the flow has completed or failed
        """
        self.logger.info('starting Engine: {')

        try:
            self.flow_graph_obj.set_context(context)
            self.flow_graph_obj.clear_steps()
            self.flow_graph_obj.mark_start()
            self._spawn_clusters(context)
            self._run_engine(context)
            self.flow_graph_obj.mark_success()
        except Exception:
            self.logger.error('Exception on starting Engine', exc_info=True)
            self.flow_graph_obj.mark_failure()
        finally:
            # TODO: do not terminate failed cluster to be able to retrieve and analyze the processing errors
            for cluster in self.execution_clusters:
                cluster.terminate()

            self.logger.info('}')

    def recover(self, context):
        """ method tries to recover the failed flow by:
            - verifying that the flow has failed before
            - spawning clusters
            - locating the failed steps and resetting their state
            - starting the flow processing from the last known successful step
            - terminating clusters after the flow has completed or failed
        """
        self.logger.info('starting Engine: {')

        try:
            self.flow_graph_obj.set_context(context)
            self.flow_graph_obj.load_steps()
            self.flow_graph_obj.mark_start()
            self._spawn_clusters(context)
            self._run_engine(context)
            self.flow_graph_obj.mark_success()
        except Exception:
            self.logger.error('Exception on starting Engine', exc_info=True)
            self.flow_graph_obj.mark_failure()
        finally:
            # TODO: do not terminate failed cluster to be able to retrieve and analyze the processing errors
            for cluster in self.execution_clusters:
                cluster.terminate()

            self.logger.info('}')
