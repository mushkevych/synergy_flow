__author__ = 'Bohdan Mushkevych'

from flow.conf import flows
from flow.core.flow_graph import FlowGraph
from flow.core.simple_actions import SleepAction, ShellCommandAction, IdentityAction, FailureAction

UNIT_TEST_FLOW_SIMPLE = 'UnitTestFlowSimple'
UNIT_TEST_FLOW_FAILURE = 'UnitTestFlowFailure'


def register_flows():
    sleep_action = SleepAction(30)
    sa_ls = ShellCommandAction('ls -al')
    sa_mkdir = ShellCommandAction('mkdir -p /tmp/trash/flows')
    sa_rmdir = ShellCommandAction('rm -Rf /tmp/trash/')
    sa_identity = IdentityAction()
    sa_failure = FailureAction()
    # pig_action = PigAction('/some/path/to/pig_script.pig')
    # export_action = ExportAction('some_postgres_table')

    flow_simple = FlowGraph(UNIT_TEST_FLOW_SIMPLE)
    flows.flows[UNIT_TEST_FLOW_SIMPLE] = flow_simple

    flow_simple.append(name='step_1',
                       dependent_on_names=[],
                       main_action=sa_rmdir, pre_actions=[sa_mkdir],
                       post_actions=[sa_ls, sleep_action, sa_mkdir])
    flow_simple.append(name='step_2',
                       dependent_on_names=['step_1'],
                       main_action=sa_rmdir, pre_actions=[sa_mkdir],
                       post_actions=[sa_ls, sleep_action, sa_mkdir])
    flow_simple.append(name='step_3',
                       dependent_on_names=['step_2'],
                       main_action=sa_rmdir, pre_actions=[sa_mkdir],
                       post_actions=[sa_ls, sleep_action, sa_mkdir])
    flow_simple.append(name='step_4',
                       dependent_on_names=['step_2'],
                       main_action=sa_rmdir, pre_actions=[sa_mkdir],
                       post_actions=[sa_ls, sleep_action, sa_mkdir])
    flow_simple.append(name='step_5',
                       dependent_on_names=['step_3', 'step_4'],
                       main_action=sa_rmdir, pre_actions=[sa_mkdir],
                       post_actions=[sa_ls, sleep_action, sa_mkdir])
    flow_simple.append(name='step_6',
                       dependent_on_names=['step_2'],
                       main_action=sa_rmdir, pre_actions=[sa_mkdir],
                       post_actions=[sa_ls, sleep_action, sa_mkdir])
    flow_simple.append(name='step_7',
                       dependent_on_names=['step_6'],
                       main_action=sa_rmdir, pre_actions=[sa_mkdir],
                       post_actions=[sa_ls, sleep_action, sa_mkdir])
    flow_simple.append(name='step_8',
                       dependent_on_names=['step_7'],
                       main_action=sa_rmdir, pre_actions=[sa_mkdir],
                       post_actions=[sa_ls, sleep_action, sa_mkdir])

    flow_failure = FlowGraph(UNIT_TEST_FLOW_FAILURE)
    flows.flows[UNIT_TEST_FLOW_FAILURE] = flow_failure

    flow_failure.append(name='step_1',
                        dependent_on_names=[],
                        main_action=sa_identity, pre_actions=[sa_identity],
                        post_actions=[sa_identity, sa_identity])
    flow_failure.append(name='step_2',
                        dependent_on_names=['step_1'],
                        main_action=sa_identity, pre_actions=[sa_identity],
                        post_actions=[sa_identity, sa_identity])
    flow_failure.append(name='step_3',
                        dependent_on_names=['step_2'],
                        main_action=sa_identity, pre_actions=[sa_identity],
                        post_actions=[sa_identity, sa_identity])
    flow_failure.append(name='step_4',
                        dependent_on_names=['step_2'],
                        main_action=sa_failure, pre_actions=[sa_identity],
                        post_actions=[sa_identity, sa_identity])
    flow_failure.append(name='step_5',
                        dependent_on_names=['step_3', 'step_4'],
                        main_action=sa_identity, pre_actions=[sa_identity],
                        post_actions=[sa_identity, sa_identity])
