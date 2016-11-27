__author__ = 'Bohdan Mushkevych'

from flow.core.abstract_action import AbstractAction


class MkdirAction(AbstractAction):
    """ Filesystem action: make the target directory and all folders along the path if needed """
    def __init__(self, uri_path, bucket_name=None):
        super(MkdirAction, self).__init__('mkdir')
        self.uri_path = uri_path
        self.bucket_name = bucket_name

    def run(self, execution_cluster):
        filesystem = execution_cluster.filesystem
        filesystem.mkdir(uri_path=self.uri_path, bucket_name=self.bucket_name)


class RmdirAction(AbstractAction):
    """ Filesystem action: removes the target directory and all nested files and folders """
    def __init__(self, uri_path, bucket_name=None):
        super(RmdirAction, self).__init__('rmdir')
        self.uri_path = uri_path
        self.bucket_name = bucket_name

    def run(self, execution_cluster):
        filesystem = execution_cluster.filesystem
        filesystem.rmdir(uri_path=self.uri_path, bucket_name=self.bucket_name)


class RmAction(AbstractAction):
    """ Filesystem action: removes a single file """
    def __init__(self, uri_path, bucket_name=None):
        super(RmAction, self).__init__('rm')
        self.uri_path = uri_path
        self.bucket_name = bucket_name

    def run(self, execution_cluster):
        filesystem = execution_cluster.filesystem
        filesystem.rm(uri_path=self.uri_path, bucket_name=self.bucket_name)


class CpAction(AbstractAction):
    """ Filesystem action: copies a single file/folder from location SOURCE to TARGET """
    def __init__(self, uri_source, uri_target, bucket_name_source=None, bucket_name_target=None):
        super(CpAction, self).__init__('cp')
        self.uri_source = uri_source
        self.bucket_name_source = bucket_name_source
        self.uri_target = uri_target
        self.bucket_name_target = bucket_name_target

    def run(self, execution_cluster):
        filesystem = execution_cluster.filesystem
        filesystem.cp(uri_source=self.uri_source, uri_target=self.uri_target,
                      bucket_name_source=self.bucket_name_source, bucket_name_target=self.bucket_name_target)


class MvAction(AbstractAction):
    """ Filesystem action: moves a single file/folder from location SOURCE to TARGET """
    def __init__(self, uri_source, uri_target, bucket_name_source=None, bucket_name_target=None):
        super(MvAction, self).__init__('mv')
        self.uri_source = uri_source
        self.bucket_name_source = bucket_name_source
        self.uri_target = uri_target
        self.bucket_name_target = bucket_name_target

    def run(self, execution_cluster):
        filesystem = execution_cluster.filesystem
        filesystem.mv(uri_source=self.uri_source, uri_target=self.uri_target,
                      bucket_name_source=self.bucket_name_source, bucket_name_target=self.bucket_name_target)


class CopyToLocalAction(AbstractAction):
    """ Filesystem action: copies a single file from remote SOURCE to local TARGET """
    def __init__(self, uri_source, uri_target, bucket_name_source=None, bucket_name_target=None):
        super(CopyToLocalAction, self).__init__('copyToLocal')
        self.uri_source = uri_source
        self.bucket_name_source = bucket_name_source
        self.uri_target = uri_target
        self.bucket_name_target = bucket_name_target

    def run(self, execution_cluster):
        filesystem = execution_cluster.filesystem
        filesystem.copyToLocal(uri_source=self.uri_source, uri_target=self.uri_target,
                               bucket_name_source=self.bucket_name_source, bucket_name_target=self.bucket_name_target)


class CopyFromLocalAction(AbstractAction):
    """ Filesystem action: copies a single file from local SOURCE to remote TARGET """
    def __init__(self, uri_source, uri_target, bucket_name_source=None, bucket_name_target=None):
        super(CopyFromLocalAction, self).__init__('copyFromLocal')
        self.uri_source = uri_source
        self.bucket_name_source = bucket_name_source
        self.uri_target = uri_target
        self.bucket_name_target = bucket_name_target

    def run(self, execution_cluster):
        filesystem = execution_cluster.filesystem
        filesystem.copyFromLocal(uri_source=self.uri_source, uri_target=self.uri_target,
                                 bucket_name_source=self.bucket_name_source, bucket_name_target=self.bucket_name_target)
