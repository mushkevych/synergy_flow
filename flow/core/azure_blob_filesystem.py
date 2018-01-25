__author__ = 'Bohdan Mushkevych'

from os import path

from azure.storage.blob import BlockBlobService

from flow.core.abstract_filesystem import AbstractFilesystem


class AzureBlobFilesystem(AbstractFilesystem):
    """ implementation of Azure Page Blob filesystem 
    https://docs.microsoft.com/en-us/azure/storage/blobs/storage-python-how-to-use-blob-storage#download-and-install-azure-storage-sdk-for-python"""
    def __init__(self, logger, context, **kwargs):
        super(AzureBlobFilesystem, self).__init__(logger, context, **kwargs)
        try:
            self.block_blob_service = BlockBlobService(account_name=context.settings['azure_account_name'],
                                                       account_key=context.settings['azure_account_key'],)
        except SomeAzureError as e:
            self.logger.error('Azure Credentials are NOT valid. Terminating.', exc_info=True)
            raise ValueError(e)

    def __del__(self):
        pass

    def _azure_bucket(self, bucket_name):
        if not bucket_name:
            bucket_name = self.context.settings['azure_bucket_name']
        azure_bucket = self.block_blob_service.create_container(bucket_name)
        return azure_bucket

    def mkdir(self, uri_path, bucket_name=None, **kwargs):
        azure_bucket = self._azure_bucket(bucket_name)
        folder_key = path.join(uri_path, '{0}_$folder$'.format(uri_path))
        if not azure_bucket.get_key(folder_key):
            s3_key = azure_bucket.new_key(folder_key)
            s3_key.set_contents_from_string('')

    def rmdir(self, uri_path, bucket_name=None, **kwargs):
        s3_bucket = self._azure_bucket(bucket_name)

        for key in s3_bucket.list(prefix='{0}/'.format(uri_path)):
            key.delete()

        if s3_bucket.get_key(uri_path):
            s3_bucket.delete_key(uri_path)

    def rm(self, uri_path, bucket_name=None, **kwargs):
        azure_bucket = self._azure_bucket(bucket_name)
        self.block_blob_service.delete_blob(azure_bucket, uri_path)

    def cp(self, uri_source, uri_target, bucket_name_source=None, bucket_name_target=None, **kwargs):
        s3_bucket_source = self._azure_bucket(bucket_name_source)
        s3_bucket_target = self._azure_bucket(bucket_name_target)
        s3_bucket_target.copy_key(new_key_name=uri_target,
                                  src_bucket_name=s3_bucket_source.name,
                                  src_key_name=uri_source)

    def mv(self, uri_source, uri_target, bucket_name_source=None, bucket_name_target=None, **kwargs):
        self.cp(uri_source, uri_target, bucket_name_source, bucket_name_target, **kwargs)
        self.rm(uri_source, bucket_name_source)

    def copyToLocal(self, uri_source, uri_target, bucket_name_source=None, **kwargs):
        azure_bucket_source = self._azure_bucket(bucket_name_source)
        with open(uri_target) as file_pointer:
            self.block_blob_service.get_blob_to_path(azure_bucket_source, uri_source, file_pointer)

    def copyFromLocal(self, uri_source, uri_target, bucket_name_target=None, **kwargs):
        azure_bucket_target = self._azure_bucket(bucket_name_target)
        with open(uri_source) as file_pointer:
            self.block_blob_service.create_blob_from_path(azure_bucket_target, file_pointer)
