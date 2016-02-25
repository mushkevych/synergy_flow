__author__ = 'Bohdan Mushkevych'


class Instantiable(object):
    """ instance of this class is passed as a parameter and holds definitions of the class to instantiate
        along with kwargs passed to the init method """

    def __init__(self, klass, kwargs=None):
        self.kwargs = {} if not kwargs else kwargs

        self.klass = klass
        self.kwargs = kwargs

    def instantiate(self):
        return self.klass(**self.kwargs)
