import os.path as p
import pkgutil
import traceback
import unittest

import tests.helper.logging_helper as lh

def load_folder(testcase, root, pkg):
    path = [p.join(root, pkg.replace(".", "/") + "/")]
    for importer, module_name, is_pkg in pkgutil.iter_modules(path):
        module = "%s.%s" % (pkg, module_name)
        if not is_pkg and importer is not None:
            try:
                __import__(module)
            except:
                testcase.fail("Failed to import module %s\n\nImport Exception Traceback:\n\n%s" %
                                (module, traceback.format_exc()))
        if is_pkg:
            load_folder(testcase, root, module)




class ImportingModulesTest(lh.LoggingTestCase):

    def setUp(self):
        self.root = p.abspath(".")

    def test_lib(self):
        load_folder(self, self.root, "lib")

    def test_roles(self):
        load_folder(self, self.root, "roles")
