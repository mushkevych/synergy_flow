__author__ = 'Bohdan Mushkevych'

import copy

from flow.flow_constants import STEP_NAME_START, STEP_NAME_FINISH
from flow.core.abstract_action import AbstractAction
from flow.core.flow_graph import FlowGraph
from flow.core.flow_graph_node import FlowGraphNode
from flow.db.model import flow
from flow.mx.terminal_graph_node import TerminalGraphNode
from flow.mx.rest_model import *


def create_rest_action(action_obj):
    assert isinstance(action_obj, AbstractAction)
    rest_model = RestAction(
        action_name=action_obj.action_name,
        kwargs=action_obj.kwargs
    )
    return rest_model


def create_rest_step(graph_node_obj):
    assert isinstance(graph_node_obj, FlowGraphNode)
    rest_model = RestStep(
        step_name=graph_node_obj.step_name,
        is_pre_completed=graph_node_obj.step_executor.is_pre_completed,
        is_main_completed=graph_node_obj.step_executor.is_main_completed,
        is_post_completed=graph_node_obj.step_executor.is_post_completed,
        pre_actions=[create_rest_action(x).document for x in graph_node_obj.step_executor.pre_actions],
        main_action=create_rest_action(graph_node_obj.step_executor.main_action),
        post_actions=[create_rest_action(x).document for x in graph_node_obj.step_executor.post_actions],
        previous_nodes=[x.step_name for x in graph_node_obj._prev],
        next_nodes=[x.step_name for x in graph_node_obj._next]
    )

    step_entry = graph_node_obj.step_entry
    if step_entry:
        rest_model.db_id = step_entry.db_id
        rest_model.flow_name = step_entry.flow_name
        rest_model.timeperiod = step_entry.timeperiod
        rest_model.state = step_entry.state
        rest_model.created_at = step_entry.created_at
        rest_model.started_at = step_entry.started_at
        rest_model.finished_at = step_entry.finished_at
        rest_model.related_flow = step_entry.related_flow

    return rest_model


def create_rest_flow(flow_graph_obj):
    assert isinstance(flow_graph_obj, FlowGraph)
    flow_entry = flow_graph_obj.context.flow_entry

    steps = dict()
    for step_name, graph_node_obj in flow_graph_obj._dict.items():
        rest_model = create_rest_step(graph_node_obj)
        steps[step_name] = rest_model.document

    graph = dict()
    graph[STEP_NAME_START] = create_rest_step(TerminalGraphNode(STEP_NAME_START)).document
    graph[STEP_NAME_FINISH] = create_rest_step(TerminalGraphNode(STEP_NAME_FINISH)).document

    for step_name, rest_step_doc in steps.items():
        graph[step_name] = copy.deepcopy(rest_step_doc)
        if not graph[step_name].get(FIELD_PREVIOUS_NODES):
            graph[step_name][FIELD_PREVIOUS_NODES] = [STEP_NAME_START]
            graph[STEP_NAME_START][FIELD_NEXT_NODES].append(step_name)

        if not graph[step_name].get(FIELD_NEXT_NODES):
            graph[step_name][FIELD_NEXT_NODES] = [STEP_NAME_FINISH]
            graph[STEP_NAME_FINISH][FIELD_PREVIOUS_NODES].append(step_name)

    rest_flow = RestFlow(
        flow_name=flow_graph_obj.flow_name,
        timeperiod='NA' if not flow_graph_obj.context.timeperiod else flow_graph_obj.context.timeperiod,
        state=flow.STATE_EMBRYO if not flow_entry else flow_entry.state,
        steps=steps,
        graph=graph
    )

    if flow_entry:
        rest_flow.db_id = flow_entry.db_id
        rest_flow.created_at = flow_entry.created_at
        rest_flow.started_at = flow_entry.started_at
        rest_flow.finished_at = flow_entry.finished_at

    return rest_flow
