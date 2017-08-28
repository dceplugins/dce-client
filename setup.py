#!/usr/bin/env python
from __future__ import print_function

import codecs
import os

from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

requirements = [
    'docker >= 2.5.1',
    'semantic-version >= 2.6.0'
]

extras_require = {}

version = None
exec (open('dce/version.py').read())

with open('./test-requirements.txt') as test_reqs_txt:
    test_requirements = [line for line in test_reqs_txt]

long_description = ''
try:
    with codecs.open('./README.rst', encoding='utf-8') as readme_rst:
        long_description = readme_rst.read()
except IOError:
    # README.rst is only generated on release. Its absence should not prevent
    # setup.py from working properly.
    pass

setup(
    name="dce",
    version=version,
    description="Python library for DaoCloud Enterprise API.",
    long_description=long_description,
    url='https://github.com/dceplugins/dce-client',
    packages=find_packages(exclude=["tests.*", "tests"]),
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require=extras_require,
    zip_safe=False,
    test_suite='tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ],
    maintainer='Cai Renjie',
    maintainer_email='revol.cai@gmail.com',
)
