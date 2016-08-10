__author__ = 'Bohdan Mushkevych'

import boto
import boto.s3
import boto.s3.key
from boto.exception import S3ResponseError
from flow.core.abstract_filesystem import AbstractFilesystem


class S3Filesystem(AbstractFilesystem):
    """ implementation of AWS S3 filesystem """
    def __init__(self, name, context, **kwargs):
        super(S3Filesystem, self).__init__(name, context, **kwargs)
        try:
            self.s3_connection = boto.connect_s3(self.settings['aws_access_key_id'],
                                                 self.settings['aws_secret_access_key'])
            self.s3_bucket = self.s3_connection.get_bucket(self.settings['aws_s3_bucket'])
        except S3ResponseError as e:
            self.logger.error('AWS Credentials are NOT valid. Terminating.', exc_info=True)
            raise ValueError(e)

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
        pass

    def copyFromLocal(self, uri_source, uri_target, **kwargs):
        with open(uri_source) as file_source:
            s3_key = boto.s3.key.Key(self.s3_bucket)
            s3_key.key = uri_target
            s3_key.set_contents_from_file(fp=file_source, rewind=True)
