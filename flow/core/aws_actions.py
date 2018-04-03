__author__ = 'Bohdan Mushkevych'

import os
import shutil
import tempfile

import psycopg2

from flow.core.execution_context import valid_context
from flow.core.abstract_action import AbstractAction


class ExportAction(AbstractAction):
    """ performs UNLOAD from the selected Postgres DB
        to the local filesystem and to S3 afterwards """
    def __init__(self, table_name, **kwargs):
        super(ExportAction, self).__init__('postgres->s3 export action', kwargs)

        self.table_name = table_name
        self.tempdir_copying = tempfile.mkdtemp()

    def set_context(self, context, step_name=None, **kwargs):
        super(ExportAction, self).set_context(context, step_name, **kwargs)

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

    @valid_context
    def run(self, execution_cluster):
        file_uri = self.table_to_file()
        if not file_uri:
            raise UserWarning('Table {0} was not exported. Aborting the action'.format(self.table_name))
        target_file_uri = '{0}/{1}.csv'.format(self.timeperiod, self.table_name)
        execution_cluster.filesystem.mkdir(self.timeperiod)
        execution_cluster.filesystem.copyFromLocal(file_uri, target_file_uri)
