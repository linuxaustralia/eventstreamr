import unittest
import os.path

import eventstreamr2.configuration.loader as loader
import eventstreamr2.configuration as cfg

class load_config_fileTestCase(unittest.TestCase):

    def setUp(self):
        self.mgr = cfg.ConfigurationManager()
        self.pk = self.mgr._priority_key
        self.path, _ = os.path.split(os.path.realpath(__file__))

    def get_file(self, name):
        return os.path.join(self.path, name)

    def test_full_argument_set_no_prio_in_file(self):
        name = "Freddie"
        priority = 100
        fname = self.get_file("loader_single_config.json")

        loader.load_config_file(self.mgr, fname, name, priority)

        self.assertEqual(self.mgr._configs[name]["service1"]["complex"],
                    {"key1": "value", "key2": "value"})
        self.assertEqual(self.mgr._configs[name][self.pk], priority)

    def test_missing_priority_no_prio_in_file(self):
        name = "Freddie"
        fname = self.get_file("loader_single_config.json")

        loader.load_config_file(self.mgr, fname, name)

        self.assertNotIn(self.pk, self.mgr._configs[name]["service1"])
        self.assertEqual(self.mgr._configs[name]["service1"]["complex"],
                    {"key1": "value", "key2": "value"})

    def test_full_argument_set_prio_in_file(self):
        name = "Freddie"
        priority = 100
        fname = self.get_file("loader_single_config_priority.json")

        loader.load_config_file(self.mgr, fname, name, priority)

        self.assertEqual(self.mgr._configs[name]["service1"]["complex"],
                    {"key1": "value", "key2": "value"})
        self.assertEqual(self.mgr._configs[name][self.pk], priority)

    def test_missing_priority_prio_in_file(self):
        name = "Freddie"
        fname = self.get_file("loader_single_config_priority.json")

        loader.load_config_file(self.mgr, fname, name)

        self.assertEqual(self.mgr._configs[name][self.pk], 50)
        self.assertEqual(self.mgr._configs[name]["service1"]["complex"],
                    {"key1": "value", "key2": "value"})
