__author__ = 'Bohdan Mushkevych'

from flow.core.abstract_filesystem import AbstractFilesystem


class EphemeralFilesystem(AbstractFilesystem):
    """ implementation of local filesystem """
    def __init__(self, name, context, **kwargs):
        super(EphemeralFilesystem, self).__init__(name, context, **kwargs)

    def __del__(self):
        pass

    def mkdir(self, uri_path, **kwargs):
        pass

    def rmdir(self, uri_path, **kwargs):
        pass

    def cp(self, uri_source, uri_target, **kwargs):
        pass

    def mv(self, uri_source, uri_target, **kwargs):
        pass

    def chmod(self, uri_file, mode, **kwargs):
        pass

    def chown(self, uri_file, owner, **kwargs):
        pass

    def copyToLocal(self, uri_source, uri_target, **kwargs):
        return self.cp(uri_source, uri_target, **kwargs)

    def copyFromLocal(self, uri_source, uri_target, **kwargs):
        return self.cp(uri_source, uri_target, **kwargs)
