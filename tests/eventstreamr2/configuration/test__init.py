import unittest

import eventstreamr2.configuration as cfg

class ConfigurationManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.mgr = cfg.ConfigurationManager()

    def test_add(self):
        cfg = {"hello": 1}
        self.mgr.set_config("service_name", "source_name", 1, cfg)

        self.assertIn("source_name", self.mgr._configs)
        self.assertIn("service_name", self.mgr._configs["source_name"])
        self.assertIn(self.mgr._priority_key, self.mgr._configs["source_name"])

        self.assertEqual(1, self.mgr._configs["source_name"][self.mgr._priority_key])
        self.assertEqual(cfg, self.mgr._configs["source_name"]["service_name"])

    def test_add_without_priority(self):
        cfg = {"hello": 1}
        self.mgr.set_config("service_name", "source_name", cfg)

        self.assertIn("source_name", self.mgr._configs)
        self.assertIn("service_name", self.mgr._configs["source_name"])
        self.assertNotIn(self.mgr._priority_key, self.mgr._configs["source_name"])

        self.assertEqual(cfg, self.mgr._configs["source_name"]["service_name"])

    def test_add_duplicate(self):
        self.mgr.set_config("service_name", "source_name", -1000, {"I don't exist":"Really"})
        # The above should be overwritten below.
        cfg = {"hello": 1}
        self.mgr.set_config("service_name", "source_name", 1, cfg)

        self.assertEqual(1, self.mgr._configs["source_name"][self.mgr._priority_key])
        self.assertEqual(cfg, self.mgr._configs["source_name"]["service_name"])

    def test_delete_source(self):
        self.mgr.set_config("service_name", "source_name", 1, {"k":"v"})
        self.mgr.set_config("service_name2", "source_name", 1, {"k":"v"})
        self.mgr.delete_source("source_name")
        self.assertEqual({}, self.mgr._configs)


    def test_delete_service_config_remove_source_service(self):
        self.mgr.set_config("service_name", "source_name", 1, {"k":"v1"})
        self.mgr.delete_service_config("service_name", "source_name")
        self.assertIn("source_name", self.mgr._configs)
        self.assertEqual({self.mgr._priority_key: 1}, self.mgr._configs["source_name"])


class ServiceConfigurationWrapperTestCase(unittest.TestCase):

    def setUp(self):
        self.mgr = cfg.ConfigurationManager()
        self.wr = self.mgr.get_config("service_name")

    def test_empty(self):
        self.assertEqual(0, len(self.wr))
        self.assertEqual(set(), self.wr.keys())
        self.assertEqual({}, dict(self.wr))
        for key in self.wr:
            self.assertFalse(True, "Key exists! %r" % key)

    def test_add_unrealted_service(self):
        self.mgr.set_config("Another Service Name", "source_name", 1, {"I don't exist":"Really"})
        self.test_empty()

    def test_add_service_without_priority(self):
        self.mgr.set_config("service_name", "source_name", {"k": "v"})
        # Ignore all sources without a priority.
        self.test_empty()

    def test_add_related_service(self):
        self.mgr.set_config("service_name", "source_name", 1, {"hello": 1})
        self.assertEqual(1, len(self.wr))
        self.assertEqual({"hello": 1}, dict(self.wr))
        self.assertEqual(1, self.wr["hello"])
        self.assertEqual(1, self.wr.get("hello"))
        self.assertEqual([1], self.wr.all("hello"))

    def test_add_2_related_service(self):
        self.mgr.set_config("service_name", "source_name", 1, {"hello": 1, "world": 1})
        self.mgr.set_config("service_name", "source_name2", 10, {"hello": 2})
        self.assertEqual([{'hello': 2}, {'world': 1, 'hello': 1}],
                            list(self.wr._ordered_configs()))
        self.assertEqual({"hello", "world"}, self.wr.keys())
        self.assertEqual(2, len(self.wr.keys()))
        self.assertEqual(2, len(self.wr))
        self.assertEqual({"hello": 2, "world": 1}, dict(self.wr))
        self.assertEqual(2, self.wr["hello"])
        self.assertEqual(1, self.wr["world"])
        self.assertEqual([2, 1], self.wr.all("hello"))
        self.assertEqual([1], self.wr.all("world"))

    def test_get_default(self):
        self.assertEqual("Pythonic!", self.wr.get("I DON'T EXIST", "Pythonic!"))
        self.assertEqual([], self.wr.all("I DON'T EXIST"))
        with self.assertRaises(KeyError):
            self.wr["I DON'T EXIST"]
