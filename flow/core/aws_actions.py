__author__ = 'Bohdan Mushkevych'

import os
import shutil
import tempfile

import boto
import boto.s3
import boto.s3.key
import psycopg2
from boto.exception import S3ResponseError

from flow.core.abstract_action import AbstractAction
from flow.core.abstract_cluster import AbstractCluster


class ExportAction(AbstractAction):
    """ performs UNLOAD from the selected Postgres DB
        to the local filesystem and to S3 afterwards """
    def __init__(self, table_name, **kwargs):
        super(ExportAction, self).__init__('postgres->s3 export action', kwargs)

        self.table_name = table_name
        self.tempdir_copying = tempfile.mkdtemp()
        self.s3_connection = None
        self.s3_bucket = None

    def set_context(self, context, step_name=None, **kwargs):
        super(ExportAction, self).set_context(context, step_name, **kwargs)
        try:
            self.s3_connection = boto.connect_s3(self.settings['aws_access_key_id'],
                                                 self.settings['aws_secret_access_key'])
            self.s3_bucket = self.s3_connection.get_bucket(self.settings['aws_s3_bucket'])
        except S3ResponseError as e:
            self.logger.error('AWS Credentials are NOT valid. Terminating.', exc_info=True)
            self.__del__()
            raise ValueError(e)

    def cleanup(self):
        """ method verifies if temporary folder exists and removes it (and nested content) """
        if self.tempdir_copying:
            self.logger.info('Cleaning up {0}'.format(self.tempdir_copying))
            shutil.rmtree(self.tempdir_copying, True)
            self.tempdir_copying = None

    def get_file(self):
        file_uri = os.path.join(self.tempdir_copying, self.table_name + '.csv')
        return open(file_uri, 'w+')  # writing and reading

    def table_to_file(self):
        """ method connects to the remote PostgreSQL and copies requested table into a local file """
        self.logger.info('Executing COPY_TO command for {0}.{1}\n.'
                         .format(self.settings['aws_redshift_db'], self.table_name))

        with psycopg2.connect(host=self.settings['aws_postgres_host'],
                              database=self.settings['aws_postgres_db'],
                              user=self.settings['aws_postgres_user'],
                              password=self.settings['aws_postgres_password'],
                              port=self.settings['aws_postgres_port']) as conn:
            with conn.cursor() as cursor:
                try:
                    f = self.get_file()
                    # http://initd.org/psycopg/docs/cursor.html#cursor.copy_to
                    cursor.copy_to(file=f, table=self.table_name, sep=',', null='null')
                    self.logger.info('SUCCESS for {0}.{1} COPY_TO command. Status message: {2}'
                                     .format(self.settings['aws_redshift_db'], self.table_name,
                                             cursor.statusmessage))
                    return f
                except Exception:
                    self.logger.error('FAILURE for {0}.{1} COPY command.'
                                      .format(self.settings['aws_redshift_db'], self.table_name), exc_info=True)
                    return None

    def file_to_s3(self, file_uri):
        """ moves exported file into the S3 """
        self.logger.info('--> Processing table export file %s' % file_uri.name)

        # copy file to S3
        s3_key = boto.s3.key.Key(self.s3_bucket)
        s3_key.key = self.timeperiod + '/' + self.table_name + '.csv'
        s3_key.set_contents_from_file(fp=file_uri, rewind=True)

    def do(self, execution_cluster):
        assert self.is_context_set is True
        file_uri = self.table_to_file()
        if not file_uri:
            raise UserWarning('Table {0} was not exported. Aborting the action'.format(self.table_name))
        self.file_to_s3(file_uri)


class PigAction(AbstractAction):
    """ executes a pig script on the given cluster """
    def __init__(self, uri_script, **kwargs):
        super(PigAction, self).__init__('EMR Pig Action', kwargs)
        self.uri_script = uri_script

    def do(self, execution_cluster):
        assert self.is_context_set is True
        assert isinstance(execution_cluster, AbstractCluster)

        is_successful = execution_cluster.run_pig_step(
            uri_script=os.path.join(self.settings['s3_pig_lib_path'], self.uri_script),
            s3_input_path='s3://synergy',
            s3_output_path=self.settings['s3_output_bucket'])
        if not is_successful:
            raise UserWarning('Pig Action failed on {0}'.format(self.uri_script))
