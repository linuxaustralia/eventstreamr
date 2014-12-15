#!/usr/bin/env python
from __future__ import print_function

import sys
import os.path
import subprocess

def main():
    """
    This is the most horrible way I could have done this. Please forgive me.
    """

    print(sys.executable)

    if "api" in sys.argv:
        subprocess.call(["pydoctor", "--html-output=-apidocs", "--make-html",
                         "--project-name=Conference Manager",
                         "--add-package=confmgr"])
    if "lint" in sys.argv:
        subprocess.call(["pylint", "-E", "confmgr", "lib"])
    if "test" in sys.argv:
        subprocess.call([sys.executable, "-tt", "-B", "-m", "unittest", "discover"])
    if "docs" in sys.argv:
        subprocess.call(["make", "html"], cwd=os.path.abspath("docs/"))
    if "tidy" in sys.argv:
        # Not lists because running in shell.
        subprocess.call(["find . -name '*.pyc' -delete"], shell=True)
        subprocess.call(["find . -name '.DS_Store' -delete"], shell=True)
        subprocess.call(["rm", "-rf", "logs", "logs-temp"])







if __name__ == "__main__":
    main();
