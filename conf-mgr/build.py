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
        subprocess.call(["python", "-m", "unittest", "discover"])








if __name__ == "__main__":
    main();
