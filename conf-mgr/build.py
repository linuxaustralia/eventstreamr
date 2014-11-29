#!/usr/bin/env python
from __future__ import print_function

import sys
import subprocess

def main():
    """
    This is the most horrible way I could have done this. Please forgive me.
    """
    if "docs" in sys.argv:
        subprocess.call(["pydoctor", "--make-html", "--project-name=Conference Manager",
                         "--add-package=lib", "--add-package=roles"])
    if "lint" in sys.argv:
        subprocess.call(["flake8", "--statistics", "lib", "roles", "scripts"])
    if "test" in sys.argv:
        subprocess.call(["python", "-tt", "-B", "-m", "unittest", "discover"])
    if "tidy" in sys.argv:
        # Not lists because running in shell.
        subprocess.call(["rm **/**.pyc"], shell=True)
        subprocess.call(["rm **/.DS_Store"], shell=True)
        subprocess.call(["rm", "-rf", "logs", "logs-temp"])








if __name__ == "__main__":
    main();
