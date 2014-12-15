#!/usr/bin/env python
from __future__ import print_function

import subprocess
import sys
import os

def which(executable):
  return 0 == subprocess.call(["which", "-s", executable])

def exit(reason, code=-1):
  print(reason, file=sys.stderr)
  print("Exiting with code", code, file=sys.stderr)
  sys.exit(code)



def elevate_privileges():
  # Modified from http://stackoverflow.com/a/5222710/369021
  sudo_exit_code = 0
  with open(os.devnull, 'w') as fnull:
    sudo_exit_code = subprocess.call(["sudo", "-n", "false"])
  # Exit code is 1 if `false` ran. 0 otherwise
  if sudo_exit_code == 0:
    print("Elevating Privileges. Please enter your password ...")
    # Relaunch using sudo.'-E',
    args = ['sudo', '-E', sys.executable] + sys.argv + ["--elevated"] + [os.environ]
    os.execlpe(*args);
  else:
    print("Running as Sudo")

def check_privilege():
  if "--elevated" in sys.argv:
    with open(os.devnull, 'w') as fnull:
      # This program was run from within `elevate_privledges`, so de-elevate them.
      subprocess.call(["sudo", "-k"], stdout=fnull, stderr=fnull)


def main():
  try:
    elevate_privileges();
    import packages

    packages.install_packages();
  finally:
    check_privilege();

#





# apt-get perlmagick xvfb ffmpeg
#
# chmod -R a+rwx /localbackup
#
# # Ensure the ssh key is accepted.
# ssh 10.4.4.3


if __name__ == "__main__":
  main();
