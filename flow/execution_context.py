__author__ = 'Bohdan Mushkevych'

from Queue import Queue


class ExecutionContext(object):
    def __init__(self, timeperiod, settings):
        assert isinstance(settings, dict)

        self.timeperiod = timeperiod
        self.settings = settings

        # multi-threading queue
        self.cluster_queue = Queue()
