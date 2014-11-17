#!/usr/bin/env false
from __future__ import print_function
from install import which, exit
import subprocess

def create_ssh_keys():
  # This won't work because `sudo`
  #  subprocess.call(["ssh-keygen", "-t", "rsa", "-N", "\"\"", "-f", "~/.ssh/id_rsa"])
  pass
