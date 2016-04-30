__author__ = 'Bohdan Mushkevych'

from flow.conf import flows
from flow.core.flow_graph import FlowGraph
from flow.core.simple_actions import SleepAction, ShellCommandAction
from flow.core.aws_actions import PigAction, ExportAction

UNIT_TEST_FLOW_SIMPLE = 'UnitTestFlowSimple'
UNIT_TEST_FLOW_COMPLEX = 'UnitTestFlowSimple'


def register_flows():
    sleep_action = SleepAction(30)
    shell_action = ShellCommandAction('ls -al')
    pig_action = PigAction('/some/path/to/pig_script.pig')
    export_action = ExportAction('some_postgres_table')

    flow_simple = FlowGraph(UNIT_TEST_FLOW_SIMPLE)
    flow_simple.append(name='step_1',
                       dependent_on_names=[],
                       main_action=pig_action, pre_actions=export_action,
                       post_actions=[shell_action, sleep_action, export_action])
    flow_simple.append(name='step_2',
                       dependent_on_names='step_1',
                       main_action=pig_action, pre_actions=export_action,
                       post_actions=[shell_action, sleep_action, export_action])
    flow_simple.append(name='step_3',
                       dependent_on_names='step_2',
                       main_action=pig_action, pre_actions=export_action,
                       post_actions=[shell_action, sleep_action, export_action])
    flow_simple.append(name='step_4',
                       dependent_on_names='step_2',
                       main_action=pig_action, pre_actions=export_action,
                       post_actions=[shell_action, sleep_action, export_action])
    flow_simple.append(name='step_5',
                       dependent_on_names=['step_3', 'step_4'],
                       main_action=pig_action, pre_actions=export_action,
                       post_actions=[shell_action, sleep_action, export_action])

    flows[UNIT_TEST_FLOW_SIMPLE] = flow_simple
