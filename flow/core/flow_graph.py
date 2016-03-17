__author__ = 'Bohdan Mushkevych'

import time
from collections import OrderedDict
from datetime import datetime

from flow.core.execution_context import ContextDriven
from flow.core.execution_step import ExecutionStep
from flow.core.flow_graph_node import FlowGraphNode
from flow.db.dao.flow_dao import FlowDao
from flow.db.dao.step_dao import StepDao

from model.flow import Flow, STATE_REQUESTED, STATE_INVALID, STATE_PROCESSED


class GraphError(Exception):
    pass


class FlowGraph(ContextDriven):
    """ Graph of interconnected Nodes, each representing an execution step """
    def __init__(self, flow_name):
        super(FlowGraph, self).__init__(flow_name)
        self.flow_name = flow_name
        self._dict = OrderedDict()
        self.flow_dao = None
        self.yielded = list()

    def __getitem__(self, key):
        return self._dict[key]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        """ heart of the Flow: traverses the graph and returns next available Node for processing
            in case all nodes are blocked - blocks by sleeping
            in case all nodes have been yielded for processing - throws a StopIteration exeption
        """
        def _next_iteration():
            if len(self.yielded) == len(self):
                # all of the nodes have been yielded for processing
                raise StopIteration()

            for name in self._dict:
                if not self.is_step_unblocked(name) or name in self.yielded:
                    continue

                self.yielded.append(name)
                return name
            return None

        while True:
            next_step_name = _next_iteration()
            while next_step_name is None:
                # at this point, there are Steps that are blocked, and we must wait for them to become available
                time.sleep(5)  # 5 seconds
                next_step_name = self.next()
            yield next_step_name

    def __eq__(self, other):
        return self._dict == other._dict

    def __contains__(self, item):
        return item in self._dict

    def append(self, name, dependent_on_names, main_action, pre_actions=None, post_actions=None, **kwargs):
        """ method appends a new Node to the Graph,
            validates the input for non-existent references
            :return self to allow chained *append*
        """
        def _find_non_existant(names):
            non_existent = list()
            for name in names:
                if name in self:
                    continue
                non_existent.append(name)
            return non_existent

        if not _find_non_existant(dependent_on_names):
            raise GraphError('Step {0} from Flow {1} is dependent on a non-existent Step {2}'
                             .format(name, self.flow_name, dependent_on_names))

        node = FlowGraphNode(name, dependent_on_names, ExecutionStep(name=name,
                                                                     main_action=main_action,
                                                                     pre_actions=pre_actions,
                                                                     post_actions=post_actions,
                                                                     kwargs=kwargs))

        # link newly inserted node with the dependent_on nodes
        for name in dependent_on_names:
            self[name]._next.append(node)
            node._prev.append(self[name])
        self._dict[name] = node

        # return *self* to allow chained *append*
        return self

    def is_step_unblocked(self, step_name):
        is_unblocked = True
        for prev_node in self[step_name]._prev:
            if prev_node.step_instance and not prev_node.step_instance.is_complete:
                is_unblocked = False
        return is_unblocked

    def set_context(self, context):
        super(FlowGraph, self).set_context(context)
        self.flow_dao = FlowDao(self.logger)

    def mark_start(self, context):
        """ performs flow start-up, such as db and context updates """
        self.set_context(context)

        flow_model = Flow()
        flow_model.flow_name = self.flow_name
        flow_model.timeperiod = context.timeperiod
        flow_model.created_at = datetime.utcnow()
        flow_model.started_at = datetime.utcnow()
        flow_model.state = STATE_REQUESTED

        step_dao = StepDao(self.logger)
        try:
            # remove, if exists, existing Flow and related Steps
            db_key = [flow_model.flow_name, flow_model.timeperiod]
            existing_flow = self.flow_dao.get_one(db_key)
            step_dao.remove_by_flow_id(existing_flow.db_id)
            self.flow_dao.remove(db_key)
        except LookupError:
            # no flow record for given key was present in the database
            pass
        finally:
            self.flow_dao.update(flow_model)
            context.flow_model = flow_model

    def mark_failure(self, context):
        """ perform flow post-failure activities, such as db update """
        context.flow_model.finished_at = datetime.utcnow()
        context.flow_model.state = STATE_INVALID
        self.flow_dao.update(context.flow_model)

    def mark_success(self, context):
        """ perform activities in case of the flow successful completion """
        context.flow_model.finished_at = datetime.utcnow()
        context.flow_model.state = STATE_PROCESSED
        self.flow_dao.update(context.flow_model)
