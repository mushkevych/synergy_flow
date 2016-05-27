# synergy_flow

[![PyPI version](https://img.shields.io/pypi/v/synergy_flow.svg)](https://pypi.python.org/pypi/synergy_flow)
[![Build Status](https://travis-ci.org/mushkevych/synergy_flow.svg?branch=master)](https://travis-ci.org/mushkevych/synergy_flow)

Simple Workflow Engine, capable of running on a local desktop or multiple concurrent EMR clusters

Concepts:
---------

Workflow (or Flow for simplicity) is identified by its name and processing timeperiod: [flow_name, timeperiod].
It represents a Directed Acyclic Graph (DAG), where each node is an execution step and edge
represents order of the execution. Each step consist of three groups of actions:
- pre: actions that has to be executed before the main
- main: main action (single)
- post: actions that has to be executed after the main

**NOTICE**: it is possible that the flow primary key should be extended by UOW_ID:
[flow_name, timeperiod, uow_id]


Reprocessing vs Continuation:
---------

As of version 0.4 the `ExecutionEngine` has main method `run`, which:
- spawns clusters
- locates existing flow records and purges them.
- starts the flow
- terminates clusters after the flow is completed or terminated

As of version 0.5 the `ExecutionEngine` has method `recover`, which:
- spawns clusters
- scans existing flow and identifies last known successful step
- triggers the execution from that identified step
- terminates clusters after the flow is completed or terminated


Multi-threading and Context:
---------

SynergyFlow revolves around the concept of a Context - a structure of names,
credentials and environment-specific settings for the Flow execution.

Under the hood, SynergyFlow is a multi-threaded application and thus - all of the steps/actions are re-entrant:
i.e. they behave as is their execution and state are thread-safe/thread-local.


Logging:
---------

logs are located under the `settings['log_directory']` path and resemble following structure:

    settings['log_directory']/
        /flow_name/flow_name.log
        /flow_name/step_name.log
        /flow_name/...
        /flow_name/step_name.log

step_name.log file itself is structured as:

    step        LEVEL   message
    step.action LEVEL   message


Roadmap:
---------

- add the *rollback* to `AbstractAction` interface and incorporate it into the `action's` life-cycle
- add *flows* tab to the Synergy Scheduler; MX should provide ability to reprocess/continue the flow

License:
---------

[BSD 3-Clause License.](http://en.wikipedia.org/wiki/BSD_licenses#3-clause_license_.28.22Revised_BSD_License.22.2C_.22New_BSD_License.22.2C_or_.22Modified_BSD_License.22.29)
Refer to LICENSE for details.


Git repository:
---------
[GitHub project page](https://github.com/mushkevych/synergy_flow)


Metafile:
---------

    /tests/               folder contains unit test
    /flow/                folder contains Synergy Flow egg


Wiki Links
---------
[Wiki Home Page](https://github.com/mushkevych/synergy_flow/wiki)


Os-Level Dependencies
---------
1. linux/unix
1. python 2.7+ / 3.4+
1. Synergy Scheduler
