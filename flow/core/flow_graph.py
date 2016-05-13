__author__ = 'Bohdan Mushkevych'

import time
from collections import OrderedDict
from datetime import datetime

from flow.core.execution_context import ContextDriven, get_flow_logger
from flow.core.step_executor import StepExecutor
from flow.core.flow_graph_node import FlowGraphNode
from flow.db.dao.flow_dao import FlowDao
from flow.db.dao.step_dao import StepDao

from flow.db.model.flow import Flow, STATE_REQUESTED, STATE_INVALID, STATE_PROCESSED


class GraphError(Exception):
    pass


class FlowGraph(ContextDriven):
    """ Graph of interconnected Nodes, each representing an execution step """

    def __init__(self, flow_name):
        super(FlowGraph, self).__init__()
        self.flow_name = flow_name

        # format: {step_name:String -> node:FlowGraphNode}
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
        """ heart of the Flow: traverses the graph and returns next available FlowGraphNode.name for processing
            in case all nodes are blocked - blocks by sleeping
            in case all nodes have been yielded for processing - throws a StopIteration exception
        """

        def _next_iteration():
            if len(self.yielded) == len(self):
                # all of the nodes have been yielded for processing
                raise StopIteration()

            for name in self._dict:
                if self.is_step_failed(name):
                    # one of the steps has failed
                    # thus, marking all flow as failed
                    raise StopIteration()

                if not self.is_step_unblocked(name) or name in self.yielded:
                    continue

                self.yielded.append(name)
                return name
            return None

        next_step_name = _next_iteration()
        while next_step_name is None:
            # at this point, there are Steps that are blocked, and we must wait for them to become available
            time.sleep(5)  # 5 seconds
            next_step_name = self.next()
        return next_step_name

    def __eq__(self, other):
        return self._dict == other._dict

    def __contains__(self, item):
        return item in self._dict

    def append(self, name, dependent_on_names, main_action, pre_actions=None, post_actions=None):
        """ method appends a new Node to the Graph,
            validates the input for non-existent references
            :return self to allow chained *append*
        """
        assert isinstance(dependent_on_names, list), \
            'dependent_on_names must be either a list of string or an empty list'

        def _find_non_existent(names):
            non_existent = list()
            for name in names:
                if name in self:
                    continue
                non_existent.append(name)
            return non_existent

        if _find_non_existent(dependent_on_names):
            raise GraphError('Step {0} from Flow {1} is dependent on a non-existent Step {2}'
                             .format(name, self.flow_name, dependent_on_names))

        node = FlowGraphNode(name, dependent_on_names, StepExecutor(step_name=name,
                                                                    main_action=main_action,
                                                                    pre_actions=pre_actions,
                                                                    post_actions=post_actions))

        # link newly inserted node with the dependent_on nodes
        for dependent_on_name in dependent_on_names:
            self[dependent_on_name]._next.append(node)
            node._prev.append(self[dependent_on_name])
        self._dict[name] = node

        # return *self* to allow chained *append*
        return self

    def is_step_unblocked(self, step_name):
        """
        :param step_name: name of the step to inspect
        :return: True if the step has no pending dependencies and is ready for processing; False otherwise
        """
        is_unblocked = True
        for prev_node in self[step_name]._prev:
            if prev_node.step_executor and not prev_node.step_executor.is_complete:
                is_unblocked = False
        return is_unblocked

    def is_step_failed(self, step_name):
        """
        :param step_name: name of the step to inspect
        :return: True if the step has failed (either in STATE_INVALID or STATE_CANCELED); False otherwise
        """
        node = self[step_name]
        return node.step_model and node.step_model.is_failed

    def set_context(self, context, **kwargs):
        super(FlowGraph, self).set_context(context, **kwargs)
        self.flow_dao = FlowDao(self.logger)

    def get_logger(self):
        return get_flow_logger(self.flow_name, self.settings)

    def mark_start(self):
        """ performs flow start-up, such as db and context updates """
        assert self.is_context_set is True
        flow_model = Flow()
        flow_model.flow_name = self.flow_name
        flow_model.timeperiod = self.context.timeperiod
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
            self.context.flow_model = flow_model

    def mark_failure(self):
        """ perform flow post-failure activities, such as db update """
        assert self.is_context_set is True
        self.context.flow_model.finished_at = datetime.utcnow()
        self.context.flow_model.state = STATE_INVALID
        self.flow_dao.update(self.context.flow_model)

    def mark_success(self):
        """ perform activities in case of the flow successful completion """
        assert self.is_context_set is True
        self.context.flow_model.finished_at = datetime.utcnow()
        self.context.flow_model.state = STATE_PROCESSED
        self.flow_dao.update(self.context.flow_model)
