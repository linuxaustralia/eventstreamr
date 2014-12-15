from setuptools import setup, find_packages

# From: http://stackoverflow.com/a/16624700/369021
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("build-requirements.txt")
# reqs is a list of requirement]
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='PyCon Conference Manager',
    version='0.0.2',
    url='https://github.com/leesdolphin/eventstreamr',
    description='',
    license='MIT',
    author='Lee Symes',
    author_email='leesdolphin@gmail.com',
    packages=find_packages(include=['confmgr*', 'lib*', 'roles*', 'tests*']),
    scripts=[
      # TODO add
    ],
    install_requires=reqs,
    tests_require=[],
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python'
    ],
    # TODO Investigate this:
    zip_safe=False,
)



# TODO move these to another file.
