__author__ = 'Bohdan Mushkevych'

from os import path

import boto3
import boto3.s3
from boto3.exceptions import Boto3Error
from botocore.exceptions import ClientError

from flow.core.abstract_filesystem import AbstractFilesystem


class S3Filesystem(AbstractFilesystem):
    """ implementation of AWS S3 filesystem """

    def __init__(self, logger, context, **kwargs):
        super(S3Filesystem, self).__init__(logger, context, **kwargs)
        try:
            self.s3_resource = boto3.resource(service_name='s3',
                                              aws_access_key_id=context.settings['aws_access_key_id'],
                                              aws_secret_access_key=context.settings['aws_secret_access_key'])
            self.s3_client = self.s3_resource.meta.client
        except (Boto3Error, ClientError) as e:
            self.logger.error('AWS Credentials are NOT valid. Terminating.', exc_info=True)
            raise ValueError(e)

    def __del__(self):
        pass

    def _s3_bucket(self, bucket_name):
        if not bucket_name:
            bucket_name = self.context.settings['aws_s3_bucket']
        s3_bucket = self.s3_resource.Bucket(bucket_name)
        return s3_bucket

    def mkdir(self, uri_path, bucket_name=None, **kwargs):
        s3_bucket = self._s3_bucket(bucket_name)
        folder_key = path.join(uri_path, '{0}_$folder$'.format(uri_path))
        try:
            self.s3_client.head_object(Bucket=s3_bucket.name, Key=folder_key)
        except ClientError:
            # Key not found
            s3_key = s3_bucket.Object(folder_key)
            s3_key.put(Body='')

    def rmdir(self, uri_path, bucket_name=None, **kwargs):
        s3_bucket = self._s3_bucket(bucket_name)

        objects_to_delete = [{'Key': uri_path}]
        for obj in s3_bucket.objects.filter(Prefix='{0}/'.format(uri_path)):
            objects_to_delete.append({'Key': obj.key})

        s3_bucket.delete_objects(
            Delete={
                'Objects': objects_to_delete
            }
        )

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
        try:
            s3_bucket_source.download_file(uri_source, uri_target)
        except ClientError as e:
            self.logger.error('AWS CopyToLocal Error:.', exc_info=True)
            raise ValueError(e)

    def copyFromLocal(self, uri_source, uri_target, bucket_name_target=None, **kwargs):
        s3_bucket_target = self._s3_bucket(bucket_name_target)
        try:
            s3_bucket_target.upload_file(uri_source, uri_target)
        except ClientError as e:
            self.logger.error('AWS CopyFromLocal Error:.', exc_info=True)
            raise ValueError(e)

    def exists(self, uri_path, bucket_name=None, **kwargs):
        s3_bucket = self._s3_bucket(bucket_name)
        folder_key = path.join(uri_path, '{0}_$folder$'.format(uri_path))
        for key in [uri_path, folder_key]:
            try:
                self.s3_client.head_object(Bucket=s3_bucket.name, Key=key)
                return True
            except ClientError:
                pass
        return False
