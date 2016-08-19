__author__ = 'Bohdan Mushkevych'

from os import path

import boto
import boto.s3
import boto.s3.key
from boto.exception import S3ResponseError
from flow.core.abstract_filesystem import AbstractFilesystem


class S3Filesystem(AbstractFilesystem):
    """ implementation of AWS S3 filesystem """
    def __init__(self, logger, context, **kwargs):
        super(S3Filesystem, self).__init__(logger, context, **kwargs)
        try:
            self.s3_connection = boto.connect_s3(context.settings['aws_access_key_id'],
                                                 context.settings['aws_secret_access_key'])
        except S3ResponseError as e:
            self.logger.error('AWS Credentials are NOT valid. Terminating.', exc_info=True)
            raise ValueError(e)

    def __del__(self):
        pass

    def _s3_bucket(self, bucket_name):
        if not bucket_name:
            bucket_name = self.context.settings['aws_s3_bucket']
        s3_bucket = self.s3_connection.get_bucket(bucket_name)
        return s3_bucket

    def mkdir(self, uri_path, bucket_name=None, **kwargs):
        s3_bucket = self._s3_bucket(bucket_name)
        folder_key = path.join(uri_path, '{0}_$folder$'.format(uri_path))
        if not s3_bucket.get_key(folder_key):
            s3_key = s3_bucket.new_key(folder_key)
            s3_key.set_contents_from_string('')

    def rmdir(self, uri_path, bucket_name=None, **kwargs):
        s3_bucket = self._s3_bucket(bucket_name)

        for key in s3_bucket.list(prefix='{0}/'.format(uri_path)):
            key.delete()

        if s3_bucket.get_key(uri_path):
            s3_bucket.delete_key(uri_path)

    def rm(self, uri_path, bucket_name=None, **kwargs):
        s3_bucket = self._s3_bucket(bucket_name)
        if s3_bucket.get_key(uri_path):
            s3_bucket.delete_key(uri_path)

    def cp(self, uri_source, uri_target, bucket_name_source=None, bucket_name_target=None, **kwargs):
        s3_bucket_source = self._s3_bucket(bucket_name_source)
        s3_bucket_target = self._s3_bucket(bucket_name_target)
        s3_bucket_target.copy_key(new_key_name=uri_target,
                                  src_bucket_name=s3_bucket_source.name,
                                  src_key_name=uri_source)

    def mv(self, uri_source, uri_target, bucket_name_source=None, bucket_name_target=None, **kwargs):
        self.cp(uri_source, uri_target, bucket_name_source, bucket_name_target, **kwargs)
        self.rm(uri_source, bucket_name_source)

    def copyToLocal(self, uri_source, uri_target, bucket_name_source=None, **kwargs):
        s3_bucket_source = self._s3_bucket(bucket_name_source)
        with open(uri_target) as file_pointer:
            s3_bucket_source.get_file(file_pointer)

    def copyFromLocal(self, uri_source, uri_target, bucket_name_target=None, **kwargs):
        s3_bucket_target = self._s3_bucket(bucket_name_target)
        with open(uri_source) as file_pointer:
            s3_key = boto.s3.key.Key(s3_bucket_target)
            s3_key.key = uri_target
            s3_key.set_contents_from_file(fp=file_pointer, rewind=True)
