#!/usr/bin/env bash

set -ev

setup.py build
coverage run --source=eventstreamr2 setup.py test flake8
