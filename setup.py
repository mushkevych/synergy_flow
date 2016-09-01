from distutils.core import setup

setup(name='synergy_flow',
      version='0.7',
      description='Synergy Flow',
      author='Bohdan Mushkevych',
      author_email='mushkevych@gmail.com',
      url='https://github.com/mushkevych/synergy_flow',
      packages=['flow', 'flow.conf', 'flow.core', 'flow.db',
                'flow.db.dao', 'flow.db.model', 'flow.workers', 'flow.mx'],
      package_data={'flow.mx': ['css/*', 'js/*', '*.html']},
      long_description='Synergy Flow is a workflow engine with separate concepts for Action, Step, Workflow '
                       'and Execution Cluster. Framework supports local desktop environment (for testing at least), '
                       'multiple concurrent EMR clusters, Qubole cluster.',
      license='BSD 3-Clause License',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
      ],
      requires=['synergy_scheduler', 'synergy_odm', 'mock', 'pymongo', 'boto', 'psycopg2', 'subprocess32']
      )
