from distutils.core import setup

setup(name='synergy_flow',
      version='0.6',
      description='Synergy Flow',
      author='Bohdan Mushkevych',
      author_email='mushkevych@gmail.com',
      url='https://github.com/mushkevych/synergy_flow',
      packages=['flow', 'flow.conf', 'flow.core', 'flow.db',
                'flow.db.dao', 'flow.db.model', 'flow.workers', 'flow.mx'],
      package_data={'flow.mx': ['css/*', 'js/*', '*.html']},
      long_description='Synergy Flow is a workflow engine, capable of running '
                       'on a local desktop or multiple concurrent EMR clusters.',
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
      ],
      requires=['synergy_scheduler', 'synergy_odm', 'mock', 'pymongo', 'boto', 'psycopg2', 'subprocess32']
      )
