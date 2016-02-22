__author__ = 'Bohdan Mushkevych'

import time
import concurrent.futures

from flow.flow_graph import FlowGraph
from synergy.system.data_logging import get_logger
from workers.emr_cluster import EmrCluster

NUMBER_OF_CLUSTERS = 2


def launch_cluster(logger, cluster_name):
    emr_cluster = EmrCluster(logger, cluster_name)
    emr_cluster.launch()
    return emr_cluster


def trigger_step_exec(logger, context, step_name, flow_graph, step_to_cluster):
    assert isinstance(flow_graph, FlowGraph)
    while flow_graph.is_step_blocked(step_name):
        time.sleep(5)   # 5 seconds

    execution_cluster = context.cluster_queue.get()
    step_to_cluster[step_name] = execution_cluster

    try:
        graph_node = flow_graph[step_name]
        graph_node.run(context, execution_cluster)
    except Exception:
        logger.error('Exception on step for {0} table'.format(step_name), exc_info=True)
    finally:
        context.cluster_queue.task_done()


class ExecutionEngine(object):
    """ Synergy Driver for mapreduce job:
        - spawning multiple AWS EMR Clusters
        - multiple Pig steps, some of whom are interdependent """

    def __init__(self, process_name, flow):
        self.logger = get_logger(process_name)
        self.flow = flow

        self.execution_clusters = list()

        # keeps track of steps assigned for execution on clusters
        # format {step_name: execution_cluster}
        self.step_to_cluster = dict()

    def spawn_clusters(self):
        self.logger.info('spawning clusters...')
        with concurrent.futures.ThreadPoolExecutor(max_workers=NUMBER_OF_CLUSTERS) as executor:
            future_to_emr = [executor.submit(launch_cluster, self.logger, 'EmrComputingCluster-{0}'.format(i))
                             for i in range(NUMBER_OF_CLUSTERS)]
            for future in concurrent.futures.as_completed(future_to_emr):
                try:
                    emr_cluster = future.result()
                    self.execution_clusters.append(emr_cluster)
                except Exception as exc:
                    self.logger.error('EMR Cluster launch generated an exception: {0}'.format(exc))

    def run_engine(self, context):
        self.logger.info('starting engine...')
        with concurrent.futures.ThreadPoolExecutor(max_workers=2 * NUMBER_OF_CLUSTERS) as executor:

            # Start the Pig Step and mark each future with the execution_cluster
            future_to_step = {executor.submit(trigger_step_exec, self.logger, context, step_name,
                                              self.flow, self.step_to_cluster): step_name
                              for step_name in self.flow}

            for future in concurrent.futures.as_completed(future_to_step):
                step_name = future_to_step[future]
                cluster = self.step_to_cluster[step_name]

                try:
                    is_step_complete = future.result()
                    if not is_step_complete:
                        self.logger.error('Execution Step {0} failed on a cluster {1}'
                                          .format(step_name, cluster))
                except Exception as exc:
                    self.logger.error('Execution Step generated an exception on cluster {0}: {1}'
                                      .format(cluster, exc))
                finally:
                    context.cluster_queue.put(cluster)

    def run(self, context):
        self.logger.info('starting EmrDriver: {')

        try:
            self.spawn_clusters()
            for cluster in self.execution_clusters:
                context.cluster_queue.put(cluster)
            self.run_engine(context)
        except Exception:
            self.logger.error('Exception on starting EmrDriver', exc_info=True)
        finally:
            # TODO: do not terminate failed cluster to be able to retrieve and analyze the processing errors
            for cluster in self.execution_clusters:
                cluster.terminate()

            self.logger.info('}')
