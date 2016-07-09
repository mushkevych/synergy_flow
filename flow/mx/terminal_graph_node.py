__author__ = 'Bohdan Mushkevych'

from flow.core.flow_graph_node import FlowGraphNode
from flow.core.simple_actions import IdentityAction
from flow.core.step_executor import StepExecutor


class TerminalGraphNode(FlowGraphNode):
    """ represents a Terminal Node (start, finish) in the FlowGraph """
    def __init__(self, step_name):
        dummy_executor = StepExecutor(step_name, IdentityAction())
        dummy_executor.is_pre_completed = True
        dummy_executor.is_main_completed = True
        dummy_executor.is_post_completed = True
        super(TerminalGraphNode, self).__init__(step_name, dummy_executor)
