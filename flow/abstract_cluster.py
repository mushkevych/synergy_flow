__author__ = 'Bohdan Mushkevych'


class AbstractCluster(object):
    def __init__(self, name, kwargs=None):
        self.name = name
        self.kwargs = {} if not kwargs else kwargs

    def run_pig_step(self, uri_script, **kwargs):
        pass

    def run_spark_step(self, uri_script, **kwargs):
        pass

    def run_hadoop_step(self, uri_script, **kwargs):
        pass

    def run_shell_command(self, uri_script, **kwargs):
        pass

    def launch(self):
        pass