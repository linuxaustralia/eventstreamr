#!/usr/bin/env false
from __future__ import print_function
from install import which, exit
import subprocess


def install_apt_packages():
  apt_packages = ["python-pip", # Pip - obviously
                  "python-dev", "build-essential", # For installing Twisted.
                  "perlmagick", "xvfb", "ffmpeg", "firefox"];
  if which("apt-get"):
    if 0 != subprocess.call(["apt-get", "-y", "install"] + apt_packages):
      exit("apt-get install of the following packages failed:\n\t" +
           "\n\t".join(apt_packages))
  else:
    exit("No `apt-get` executable detected.")

def install_pip_packages():
  pip_packages = ["Twisted"]
  pip_packages = pip_packages + ["Sphinx"] # Documentation.

  if which("pip"):
    if 0 != subprocess.call(["pip", "install"] + pip_packages):
      exit("pip install of the following packages failed:\n\t" +
           "\n\t".join(pip_packages))
  else:
    exit("Please install pip before continuing. See:" +
          "\n\thttps://pip.pypa.io/en/latest/installing.html")


def install_packages():
  print("Installing Packages")
  #install_apt_packages()
  install_pip_packages()
