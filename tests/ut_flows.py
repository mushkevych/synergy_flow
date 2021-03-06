__author__ = 'Bohdan Mushkevych'

from flow.conf import flows
from flow.core.flow_graph import FlowGraph
from flow.core.simple_actions import SleepAction, ShellCommandAction, IdentityAction, FailureAction
from flow.core.filesystem_actions import MkdirAction, RmdirAction

UNIT_TEST_FLOW_SIMPLE = 'UnitTestFlowSimple'
UNIT_TEST_FLOW_FAILURE = 'UnitTestFlowFailure'


def register_flows():
    sleep_action = SleepAction(30)
    sa_ls = ShellCommandAction('ls -al')
    fa_mkdir = MkdirAction('/tmp/trash/flows')
    fa_rmdir = RmdirAction('/tmp/trash/')
    sa_identity = IdentityAction()
    sa_failure = FailureAction()

    flow_simple = FlowGraph(UNIT_TEST_FLOW_SIMPLE)
    flows.flows[UNIT_TEST_FLOW_SIMPLE] = flow_simple

    flow_simple.append(name='step_1',
                       dependent_on_names=[],
                       main_action=fa_rmdir, pre_actions=[fa_mkdir],
                       post_actions=[sa_ls, sleep_action, fa_mkdir])
    flow_simple.append(name='step_2',
                       dependent_on_names=['step_1'],
                       main_action=fa_rmdir, pre_actions=[fa_mkdir],
                       post_actions=[sa_ls, sleep_action, fa_mkdir])
    flow_simple.append(name='step_3',
                       dependent_on_names=['step_2'],
                       main_action=fa_rmdir, pre_actions=[fa_mkdir],
                       post_actions=[sa_ls, sleep_action, fa_mkdir])
    flow_simple.append(name='step_4',
                       dependent_on_names=['step_2'],
                       main_action=fa_rmdir, pre_actions=[fa_mkdir],
                       post_actions=[sa_ls, sleep_action, fa_mkdir])
    flow_simple.append(name='step_5',
                       dependent_on_names=['step_3', 'step_4'],
                       main_action=fa_rmdir, pre_actions=[fa_mkdir],
                       post_actions=[sa_ls, sleep_action, fa_mkdir])
    flow_simple.append(name='step_6',
                       dependent_on_names=['step_2'],
                       main_action=fa_rmdir, pre_actions=[fa_mkdir],
                       post_actions=[sa_ls, sleep_action, fa_mkdir])
    flow_simple.append(name='step_7',
                       dependent_on_names=['step_6'],
                       main_action=fa_rmdir, pre_actions=[fa_mkdir],
                       post_actions=[sa_ls, sleep_action, fa_mkdir])
    flow_simple.append(name='step_8',
                       dependent_on_names=['step_7'],
                       main_action=fa_rmdir, pre_actions=[fa_mkdir],
                       post_actions=[sa_ls, sleep_action, fa_mkdir])

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
