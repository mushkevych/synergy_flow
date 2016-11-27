__author__ = 'Bohdan Mushkevych'

from flow.core.flow_graph_node import FlowGraphNode
from flow.core.simple_actions import IdentityAction
from flow.core.step_executor import StepExecutor, ACTIONSET_COMPLETE


class TerminalGraphNode(FlowGraphNode):
    """ represents a Terminal Node (start, finish) in the FlowGraph """
    def __init__(self, step_name):
        dummy_executor = StepExecutor(step_name, IdentityAction())
        dummy_executor.pre_actionset.state = ACTIONSET_COMPLETE
        dummy_executor.main_actionset.state = ACTIONSET_COMPLETE
        dummy_executor.post_actionset.state = ACTIONSET_COMPLETE
        super(TerminalGraphNode, self).__init__(step_name, dummy_executor)
