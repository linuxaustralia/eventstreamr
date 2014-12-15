import unittest

import tests.helper.logging_helper as lh

import roles as rl

class check_loadTest(lh.LoggingTestCase):

    def setUp(self):
        self.rl = reload(rl)

    def test_prevents_repeated_loaded(self):
        self.rl._check_load()
        self.assertTrue(self.rl._loaded_roles)
