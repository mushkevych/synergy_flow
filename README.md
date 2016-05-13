# synergy_flow

[![PyPI version](https://img.shields.io/pypi/v/synergy_flow.svg)](https://pypi.python.org/pypi/synergy_flow)
[![Build Status](https://travis-ci.org/mushkevych/synergy_flow.svg?branch=master)](https://travis-ci.org/mushkevych/synergy_flow)

Simple Workflow Engine, capable of running on a local desktop or multiple concurrent EMR clusters

Multithreading and Context:
---------

SynergyFlow revolves around the concept of Context - a structure of settings, names, credentials specific to the
environment and time of the Flow execution.


Synergy Flow is underneath the multi-threaded application, and thus - all the context are thread-local.

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
