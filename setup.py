from distutils.core import setup

setup(name='synergy_flow',
      version='0.4',
      description='Synergy Flow',
      author='Bohdan Mushkevych',
      author_email='mushkevych@gmail.com',
      url='https://github.com/mushkevych/synergy_flow',
      packages=['flow.conf', 'flow.db', 'flow.db.dao', 'flow.db.model',
                'flow.core', 'flow.workers'],
      package_data={},
      long_description='Synergy Flow is a workflow engine, capable of running '
                       'on a local desktop or multiple concurrent EMR clusters.',
      license='BSD 3-Clause License',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
      ],
      requires=['synergy_scheduler', 'synergy_odm', 'mock', 'pymongo', 'boto', 'psycopg2', 'subprocess32']
      )
