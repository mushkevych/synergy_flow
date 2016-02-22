
__author__ = 'Bohdan Mushkevych'

import os
import shutil
import tempfile

import boto
import boto.s3
import boto.s3.key
import psycopg2
from boto.exception import S3ResponseError
from synergy.conf import settings
from flow.abstract_action import AbstractAction


class ExportAction(AbstractAction):
    def __init__(self, logger, timeperiod, table_name):
        self.logger = logger
        self.timeperiod = str(timeperiod)
        self.table_name = table_name
        self.tempdir_copying = tempfile.mkdtemp()

        try:
            self.s3_connection = boto.connect_s3(settings.settings['aws_access_key_id'],
                                                 settings.settings['aws_secret_access_key'])
            self.s3_bucket = self.s3_connection.get_bucket(settings.settings['aws_copperlight_s3_bucket'])
        except S3ResponseError as e:
            self.logger.error('AWS Credentials are NOT valid. Terminating.', exc_info=True)
            self.__del__()
            raise ValueError(e)

    def __del__(self):
        self._clean_up()

    def _clean_up(self):
        """ method verifies if temporary folder exists and removes it (and nested content) """
        if self.tempdir_copying:
            self.logger.info('Cleaning up {0}'.format(self.tempdir_copying))
            shutil.rmtree(self.tempdir_copying, True)
            self.tempdir_copying = None

    def get_file(self):
        file_uri = os.path.join(self.tempdir_copying, self.table_name + '.csv')
        return file(file_uri, 'w+')  # writing and reading

    def table_to_file(self):
        """ method connects to the remote PostgreSQL and copies requested table into a local file """
        self.logger.info('Executing COPY_TO command for {0}.{1}\n.'
                         .format(settings.settings['aws_redshift_db'], self.table_name))

        with psycopg2.connect(host=settings.settings['aws_postgres_host'],
                              database=settings.settings['aws_postgres_db'],
                              user=settings.settings['aws_postgres_user'],
                              password=settings.settings['aws_postgres_password'],
                              port=settings.settings['aws_postgres_port']) as conn:
            with conn.cursor() as cursor:
                try:
                    f = self.get_file()
                    # http://initd.org/psycopg/docs/cursor.html#cursor.copy_to
                    cursor.copy_to(file=f, table=self.table_name, sep=',', null='null')
                    self.logger.info('SUCCESS for {0}.{1} COPY_TO command. Status message: {2}'
                                     .format(settings.settings['aws_redshift_db'], self.table_name,
                                             cursor.statusmessage))
                    return f
                except Exception:
                    self.logger.error('FAILURE for {0}.{1} COPY command.'
                                      .format(settings.settings['aws_redshift_db'], self.table_name), exc_info=True)
                    return None

    def file_to_s3(self, file_uri):
        """ moves exported file into the S3 """
        self.logger.info('--> Processing table export file %s' % file_uri.name)

        # copy file to S3
        s3_key = boto.s3.key.Key(self.s3_bucket)
        s3_key.key = self.timeperiod + '/' + self.table_name + '.csv'
        s3_key.set_contents_from_file(fp=file_uri, rewind=True)

    def do(self, context):
        file_uri = self.table_to_file()
        if not file_uri:
            raise UserWarning('Table {0} was not exported. Aborting the action'.format(self.table_name))
        self.file_to_s3(file_uri)
