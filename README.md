# synergy_flow

[![PyPI version](https://img.shields.io/pypi/v/synergy_flow.svg)](https://pypi.python.org/pypi/synergy_flow)
[![Build Status](https://travis-ci.org/mushkevych/synergy_flow.svg?branch=master)](https://travis-ci.org/mushkevych/synergy_flow)

Simple Workflow Engine, capable of running on a local desktop or multiple concurrent EMR clusters

Concepts:
---------

Workflow (or Flow for simplicity) is identified by its name and processing timeperiod: `[flow_name, timeperiod]`
It represents a Directed Acyclic Graph (DAG) where each node is an execution step
and edge represents dependencies between steps and hence - order of the execution.

Each step consist of three groups of actions:
- pre: actions that has to be executed before the main
- main: single main action
- post: actions that has to be executed after the main


Processing and Recovery:
---------

`ExecutionEngine` exposes two main methods:

`run`
- spawns clusters
- locates existing flow record or creates one
- purges all existing step records, if they exist
- starts the flow
- terminates clusters after the flow is completed or terminated

`recover`
- spawns clusters
- locates existing flow record or creates one
- scans for existing step records and loads all successful ones
- triggers the execution from the last successful step
- terminates clusters after the flow is completed or terminated


Context:
---------

SynergyFlow revolves around the concept of a Context - a structure of names,
credentials and environment-specific settings for the Flow execution.


Multi-threading:
---------

In production setup Synergy Flow orchestrates workflow execution on a cluster of machines.
To coordinate such plurality, it is a multi-threaded application under the hood.
From the design perspective, it requires all of the steps/actions to be re-entrant:
i.e. they behave as if their execution and state are thread-safe/thread-local.
From implementation perspective, this is achieved by deep copying of every action used by steps.


Logging:
---------

Synergy Flow provide rich logging output.
Logs are located under the `settings['log_directory']` path and resemble following structure:

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
- evaluate whether it makes sense to extend Flow **primary key** by UOW_ID:
`[flow_name, timeperiod, uow_id]`

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
