__author__ = 'Bohdan Mushkevych'

import os
import shutil

from flow.core.abstract_filesystem import AbstractFilesystem


class EphemeralFilesystem(AbstractFilesystem):
    """ implementation of local filesystem """
    def __init__(self, logger, context, **kwargs):
        super(EphemeralFilesystem, self).__init__(logger, context, **kwargs)

    def __del__(self):
        pass

    def mkdir(self, uri_path, **kwargs):
        os.makedirs(uri_path)

    def rmdir(self, uri_path, **kwargs):
        shutil.rmtree(uri_path, **kwargs)

    def rm(self, uri_path, **kwargs):
        if os.path.isdir(uri_path):
            shutil.rmtree(uri_path)
        else:
            os.remove(uri_path)

    def cp(self, uri_source, uri_target, **kwargs):
        if os.path.isdir(uri_source):
            shutil.copytree(uri_source, uri_target)
        else:
            shutil.copy(uri_source, uri_target)

    def mv(self, uri_source, uri_target, **kwargs):
        shutil.move(uri_source, uri_target)

    def copyToLocal(self, uri_source, uri_target, **kwargs):
        return self.cp(uri_source, uri_target, **kwargs)

    def copyFromLocal(self, uri_source, uri_target, **kwargs):
        return self.cp(uri_source, uri_target, **kwargs)

    def exists(self, uri_path, **kwargs):
        return os.path.exists(uri_path)
