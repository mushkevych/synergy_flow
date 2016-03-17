__author__ = 'Bohdan Mushkevych'

from flow.conf import flows
from flow.core.flow_graph import FlowGraph
from flow.core.simple_actions import SleepAction, ShellCommandAction

from flow.core.aws_actions import PigAction, ExportAction

sleep_action = SleepAction(30)
shell_action = ShellCommandAction('ls -al')
pig_action = PigAction('/some/path/to/pig_script.pig')
export_action = ExportAction('some_postgres_table')

flow_example = FlowGraph('example flow')
flow_example.append(name='example_step_1',
                    dependent_on_names=[],
                    main_action=pig_action, pre_actions=export_action,
                    post_actions=[shell_action, sleep_action, export_action])
flow_example.append(name='example_step_2',
                    dependent_on_names='example_step_1',
                    main_action=pig_action, pre_actions=export_action,
                    post_actions=[shell_action, sleep_action, export_action])

flows['FLOW_EXAMPLE'] = flow_example
