__author__ = 'Bohdan Mushkevych'

import time
from collections import OrderedDict
from datetime import datetime

from flow.flow_constants import STEP_NAME_START, STEP_NAME_FINISH
from flow.core.execution_context import ContextDriven, get_flow_logger, valid_context
from flow.core.step_executor import StepExecutor
from flow.core.flow_graph_node import FlowGraphNode
from flow.db.dao.flow_dao import FlowDao
from flow.db.dao.step_dao import StepDao
from flow.db.model.step import Step
from synergy.system.log_recording_handler import LogRecordingHandler

from flow.db.model.flow import Flow, STATE_EMBRYO, STATE_INVALID, STATE_PROCESSED, STATE_IN_PROGRESS


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
        self.log_recording_handler = None

        # list of step names, yielded for processing
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
            in case all nodes have been yielded for processing - throws StopIteration exception
            in case any node has failed - throw StopIteration exception
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

    def enlist(self, step_exec, dependent_on_names):
        assert isinstance(step_exec, StepExecutor)
        return self.append(step_exec.step_name, dependent_on_names, step_exec.main_actionset.actions,
                           step_exec.pre_actionset.actions, step_exec.post_actionset.actions, step_exec.skip)

    def append(self, name, dependent_on_names, main_action, pre_actions=None, post_actions=None, skip=False):
        """ method appends a new Node to the Graph,
            validates the input for non-existent references
            :return self to allow chained *append*
        """
        assert isinstance(dependent_on_names, list), \
            'dependent_on_names must be either a list of string or an empty list'
        assert name not in [STEP_NAME_START, STEP_NAME_FINISH], \
            'step names [{0}, {1}] are reserved.'.format(STEP_NAME_START, STEP_NAME_FINISH)

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

        node = FlowGraphNode(name, StepExecutor(step_name=name,
                                                main_action=main_action,
                                                pre_actions=pre_actions,
                                                post_actions=post_actions,
                                                skip=skip))

        # link newly inserted node with the dependent_on nodes
        for dependent_on_name in dependent_on_names:
            self[dependent_on_name]._next.append(node)
            node._prev.append(self[dependent_on_name])
        self._dict[name] = node

        # return *self* to allow chained *append*
        return self

    def all_dependant_steps(self, step_name):
        """
        :param step_name: name of the step to inspect
        :return: list of all step names, that are dependent on current step
        """
        dependent_on = list()
        for child_node in self[step_name]._next:
            dependent_on.append(child_node.step_name)
            dependent_on.extend(self.all_dependant_steps(child_node.step_name))
        return dependent_on

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
        return node.step_entry and node.step_entry.is_failed

    def set_context(self, context, **kwargs):
        super(FlowGraph, self).set_context(context, **kwargs)
        self.flow_dao = FlowDao(self.logger)

        try:
            # fetch existing Flow from the DB
            db_key = [self.flow_name, self.context.timeperiod]
            flow_entry = self.flow_dao.get_one(db_key)
        except LookupError:
            # no flow record for given key was present in the database
            flow_entry = Flow()
            flow_entry.flow_name = self.flow_name
            flow_entry.timeperiod = self.context.timeperiod
            flow_entry.created_at = datetime.utcnow()
            flow_entry.state = STATE_EMBRYO

        self.flow_dao.update(flow_entry)
        self.context.flow_entry = flow_entry

    def get_logger(self):
        return get_flow_logger(self.flow_name, self.settings)

    @valid_context
    def clear_steps(self):
        """ method purges all steps related to given flow from the DB """
        assert self.context.flow_entry is not None

        step_dao = StepDao(self.logger)
        step_dao.remove_by_flow_id(self.context.flow_entry.db_id)

    @valid_context
    def load_steps(self):
        """ method:
            1. loads all steps
            2. filters out successful and updates GraphNodes and self.yielded list accordingly
            3. removes failed steps from the DB
        """
        assert self.context.flow_entry is not None

        step_dao = StepDao(self.logger)
        steps = step_dao.get_all_by_flow_id(self.context.flow_entry.db_id)
        for s in steps:
            assert isinstance(s, Step)
            if s.is_processed:
                self[s.step_name].step_entry = s
                self.yielded.append(s.step_name)
            else:
                step_dao.remove(s.key)

    @valid_context
    def mark_start(self):
        """ performs flow start-up, such as db and context updates """
        self.context.flow_entry.started_at = datetime.utcnow()
        self.context.flow_entry.state = STATE_IN_PROGRESS
        self.flow_dao.update(self.context.flow_entry)

        # enable log recording into DB
        self.log_recording_handler = LogRecordingHandler(self.get_logger(), self.context.flow_entry.db_id)
        self.log_recording_handler.attach()

    @valid_context
    def _mark_finish(self, state):
        self.context.flow_entry.finished_at = datetime.utcnow()
        self.context.flow_entry.state = state
        self.flow_dao.update(self.context.flow_entry)

        if self.log_recording_handler:
            self.log_recording_handler.detach()

    def mark_failure(self):
        """ perform flow post-failure activities, such as db update """
        self._mark_finish(STATE_INVALID)

    def mark_success(self):
        """ perform activities in case of the flow successful completion """
        self._mark_finish(STATE_PROCESSED)
