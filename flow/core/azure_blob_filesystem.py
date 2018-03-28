__author__ = 'Bohdan Mushkevych'

from os import path

from azure.storage.blob import BlockBlobService

from flow.core.abstract_filesystem import AbstractFilesystem, splitpath


class AzureBlobFilesystem(AbstractFilesystem):
    """ implementation of Azure Page Blob filesystem 
    https://docs.microsoft.com/en-us/azure/storage/blobs/storage-python-how-to-use-blob-storage#download-and-install-azure-storage-sdk-for-python"""
    def __init__(self, logger, context, **kwargs):
        super(AzureBlobFilesystem, self).__init__(logger, context, **kwargs)
        try:
            self.block_blob_service = BlockBlobService(account_name=context.settings['azure_account_name'],
                                                       account_key=context.settings['azure_account_key'])
        except EnvironmentError as e:
            self.logger.error('Azure Credentials are NOT valid. Terminating.', exc_info=True)
            raise ValueError(e)

    def __del__(self):
        pass

    def _azure_bucket(self, bucket_name):
        if not bucket_name:
            bucket_name = self.context.settings['azure_bucket']
        return bucket_name

    def mkdir(self, uri_path, bucket_name=None, **kwargs):
        def _create_folder_file():
            folder_key = path.join(root, '{0}_$folder$'.format(folder_name))
            if not self.block_blob_service.exists(azure_bucket, folder_key):
                self.block_blob_service.create_blob_from_text(azure_bucket, folder_key, '')

        azure_bucket = self._azure_bucket(bucket_name)
        root = ''
        for folder_name in splitpath(uri_path):
            root = path.join(root, folder_name)
            _create_folder_file()

    def rmdir(self, uri_path, bucket_name=None, **kwargs):
        azure_bucket = self._azure_bucket(bucket_name)
        for key in self.block_blob_service.list_blobs(azure_bucket, prefix='{0}/'.format(uri_path)):
            self.block_blob_service.delete_blob(azure_bucket, key)

    def rm(self, uri_path, bucket_name=None, **kwargs):
        azure_bucket = self._azure_bucket(bucket_name)
        self.block_blob_service.delete_blob(azure_bucket, uri_path)

    def cp(self, uri_source, uri_target, bucket_name_source=None, bucket_name_target=None, **kwargs):
        azure_bucket_source = self._azure_bucket(bucket_name_source)
        azure_bucket_target = self._azure_bucket(bucket_name_target)
        source_blob_url = self.block_blob_service.make_blob_url(azure_bucket_source, uri_source)
        self.block_blob_service.copy_blob(azure_bucket_target, uri_target, source_blob_url)

    def mv(self, uri_source, uri_target, bucket_name_source=None, bucket_name_target=None, **kwargs):
        self.cp(uri_source, uri_target, bucket_name_source, bucket_name_target, **kwargs)
        self.rm(uri_source, bucket_name_source)

    def copyToLocal(self, uri_source, uri_target, bucket_name_source=None, **kwargs):
        azure_bucket_source = self._azure_bucket(bucket_name_source)
        with open(uri_target, 'wb') as file_pointer:
            self.block_blob_service.get_blob_to_stream(azure_bucket_source, uri_source, file_pointer)

    def copyFromLocal(self, uri_source, uri_target, bucket_name_target=None, **kwargs):
        azure_bucket_target = self._azure_bucket(bucket_name_target)
        with open(uri_source, 'rb') as file_pointer:
            self.block_blob_service.create_blob_from_stream(azure_bucket_target, uri_target, file_pointer)

    def exists(self, uri_path, bucket_name=None, exact=False, **kwargs):
        azure_bucket = self._azure_bucket(bucket_name)
        is_found = self.block_blob_service.exists(azure_bucket, uri_path)
        if exact is False and is_found is False:
            folder_name = '{0}_$folder$'.format(path.basename(uri_path))
            folder_key = path.join(uri_path, folder_name)
            is_found = self.block_blob_service.exists(azure_bucket, folder_key)
        return is_found
