import unittest

import configuration as cfg

class ConfigurationManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.mgr = cfg.ConfigurationManager()

    def test_add(self):
        cfg = {"hello": 1}
        self.mgr.set_config("123", "name", 1, cfg)

        self.assertIn("123", self.mgr.configs)
        self.assertIn("name", self.mgr.configs["123"])
        self.assertIn("priority", self.mgr.configs["123"]["name"])
        self.assertIn("config", self.mgr.configs["123"]["name"])

        self.assertEqual(1, self.mgr.configs["123"]["name"]["priority"])
        self.assertEqual(cfg, self.mgr.configs["123"]["name"]["config"])

    def test_add_duplicate(self):
        self.mgr.set_config("123", "name", -1000, {"I don't exist":"Really"})
        # The above should be overwritten below.
        cfg = {"hello": 1}
        self.mgr.set_config("123", "name", 1, cfg)

        self.assertEqual(1, self.mgr.configs["123"]["name"]["priority"])
        self.assertEqual(cfg, self.mgr.configs["123"]["name"]["config"])

    def test_delete_service(self):
        self.mgr.set_config("123", "name", -1000, {"I don't exist":"Really"})
        self.mgr.delete_config("123")
        self.assertEqual({}, self.mgr.configs)

    def test_delete_service_mgr(self):
        self.mgr.set_config("123", "name", -1000, {"I don't exist":"Really"})
        self.mgr.delete_config("123", "name")
        self.assertIn("123", self.mgr.configs)
        self.assertEqual({}, self.mgr.configs["123"])


class ServiceConfigurationWrapperTestCase(unittest.TestCase):

    def setUp(self):
        self.mgr = cfg.ConfigurationManager()
        self.wr = self.mgr.get_config("123")

    def test_empty(self):
        self.assertEqual(0, len(self.wr))
        self.assertEqual(set(), self.wr.keys())
        self.assertEqual({}, dict(self.wr))
        for key in self.wr:
            self.assertFalse(True, "Key exists! %r" % key)

    def test_add_unrealted_service(self):
        self.mgr.set_config("DIFFERENT", "name", 1, {"I don't exist":"Really"})
        self.test_empty()

    def test_add_related_service(self):
        self.mgr.set_config("123", "name", 1, {"hello": 1})
        self.assertEqual(1, len(self.wr))
        self.assertEqual({"hello": 1}, dict(self.wr))
        self.assertEqual(1, self.wr["hello"])
        self.assertEqual(1, self.wr.get("hello"))
        self.assertEqual([1], self.wr.all("hello"))

    def test_add_2_related_service(self):
        self.mgr.set_config("123", "name", 1, {"hello": 1, "world": 1})
        self.mgr.set_config("123", "name2", 10, {"hello": 2})
        self.assertEqual([{'hello': 2}, {'world': 1, 'hello': 1}], self.wr._ordered_configs())
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



if __name__ == '__main__':
    unittest.main()
