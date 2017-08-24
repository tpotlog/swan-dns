#!/usr/bin/env python

from distutils.core import setup

setup(name='swandns',
      version='1.0',
      description='Python based mosular DNS server',
      author='Tal Engel-Potlog',
      author_email='tal.potlog@gmail.com',
      url='https://github.com/tpotlog/swan-dns',
      packages=['swandns',
                'swandns.modules',
                'swandns.server',
                'swandns.swan_errors',
                'swandns.utils'],
      license='MIT'
      
     )
