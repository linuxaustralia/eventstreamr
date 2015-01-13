#!/usr/bin/env bash

set -ev

python setup.py build
coverage run --source=eventstreamr2 setup.py test flake8
