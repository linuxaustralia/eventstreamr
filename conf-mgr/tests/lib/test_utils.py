import unittest

import lib.utils as ut


class ObservableTestCase(unittest.TestCase):

    def setUp(self):
        self.obj = ut.Observable()

    def test_fires_added(self):
        called = []
        def callee():
            called.append("")
        self.obj.add_observer(callee)
        self.obj._notify_observers()
        self.assertTrue(called)

    def test_fires_with_args(self):
        called = []
        def callee(arg1):
            self.assertEqual(self, arg1)
            called.append("")
        self.obj.add_observer(callee)
        self.obj._notify_observers(self)
        self.assertTrue(called)

    def test_remove_acts_correctly(self):
        called = []
        def callee():
            called.append("")
        self.obj.add_observer(callee)
        self.obj.add_observer(callee)
        self.obj.remove_observer(callee)
        self.obj._notify_observers()
        self.assertEqual(1, len(called))


class AbstractPriorityDictionaryTestCase(unittest.TestCase):

    class SampleAbstractPriorityDictionary(ut.AbstractPriorityDictionary):
        def __init__(self, test):
            super(
                AbstractPriorityDictionaryTestCase.SampleAbstractPriorityDictionary,
                self).__init__()
            self.test = test

        def ordered_configs(self):
            return self.test.data


    def setUp(self):
        self.data = []
        self.obj = self.SampleAbstractPriorityDictionary(self)

    def test_keys_and_iter_and_length(self):
        self.data = [{"hello": 1}, {"hello": 2, "bob": 3, "jane": 4}, {"joe":5}]
        self.assertItemsEqual(self.obj.keys(), ["hello", "bob", "jane", "joe"])
        self.assertItemsEqual(self.obj, ["hello", "bob", "jane", "joe"])
        self.assertEqual(4, len(self.obj))

    def test_get_item(self):
        self.data = [{"hello": 1}, {"hello": 2, "world": 1}, {"world":2}]
        self.assertEqual(1, self.obj["hello"])
        self.assertEqual(1, self.obj["world"])
        with self.assertRaises(KeyError):
            self.obj["I don't exist"]

    def test_contains(self):
        self.data = [{"hello": 1}, {"bob": 2, "jane": 1}, {"joe":2}]
        self.assertTrue("hello" in self.obj)
        self.assertFalse("I don't exist" in self.obj)

    def test_all(self):
        self.data = [{"hello": 1}, {"hello": 2, "world": 3}, {"world":3}]
        self.assertListEqual(self.obj.all("hello"), [1,2])
        self.assertListEqual(self.obj.all("world"), [3,3])
        self.assertListEqual(self.obj.all("I don't exist"), [])


class PrioritySubDictionaryTestCase(unittest.TestCase):

    class SampleAbstractPriorityDictionary(object):
        def __init__(self, test):
            self.test = test

        def all(self, *args, **kwargs):
            return self.test.all(*args, **kwargs)

    def setUp(self):
        self.parent = self.SampleAbstractPriorityDictionary(self)

    def test_missing_key(self):
        self.all = lambda key: []
        obj = ut.PrioritySubDictionary(self.parent, "I don't exist")
        self.assertEqual(len(obj), 0)

    def test_existing_key(self):
        dict_list = [{"1": 1}, {"1": 3}, {"2": 2}]
        def a(key):
            return dict_list
        self.all = a
        obj = ut.PrioritySubDictionary(self.parent, "hello")
        self.assertListEqual(obj.ordered_configs(), dict_list)
