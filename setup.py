#!/usr/bin/env python

from setuptools import setup, find_packages

# From: http://stackoverflow.com/a/16624700/369021
from pip.req import parse_requirements
import uuid

# parse_requirements() returns generator of pip.req.InstallRequirement objects
# reqs is a list of requirement
requirements_from_file = lambda file: \
    [str(ir.req) for ir in
     parse_requirements(file, session=uuid.uuid1())]

setup(
    name='PyCon Conference Manager',
    version='0.0.2',
    url='https://github.com/leesdolphin/eventstreamr',
    description='',
    license='MIT',
    author='Lee Symes',
    author_email='leesdolphin@gmail.com',
    packages=find_packages(include=['eventstreamr2*']),
    scripts=[
            # TODO add
    ],
    install_requires=requirements_from_file("build-requirements.txt"),
    tests_require=requirements_from_file("test-requirements.txt"),
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python'
    ],
    setup_requires=['flake8'],
    # TODO Investigate this:
    zip_safe=False,
)
