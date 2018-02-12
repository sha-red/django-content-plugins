#!/usr/bin/env python

from io import open
import os
from setuptools import setup, find_packages


def get_version(prefix):
    import re
    with open(os.path.join(prefix, '__init__.py')) as fd:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fd.read()))
    return metadata['version']


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, encoding='utf-8') as handle:
        return handle.read()


setup(
    name='django-content-plugins',
    version=get_version('content_plugins'),
    description='',
    long_description=read('README.md'),
    author='Erik Stein',
    author_email='erik@classlibrary.net',
    url='https://projects.c--y.net/erik/django-content-plugins/',
    license='MIT License',
    platforms=['OS Independent'],
    packages=find_packages(
        exclude=['tests', 'testapp'],
    ),
    include_package_data=True,
    install_requires=[
        # 'django<2', commented out to make `pip install -U` easier
        'django-content-editor',
        'feincms3',
    ],
    classifiers=[
        # "Development Status :: 3 - Alpha",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    zip_safe=False,
)
