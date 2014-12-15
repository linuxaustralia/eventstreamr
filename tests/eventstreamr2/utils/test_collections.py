import unittest

import eventstreamr2.utils.collections as ut



class WeakFunctionCollectionTestCase(unittest.TestCase):

    def setUp(self):
        self.l = ut.WeakFunctionCollection()

    def test_bound_method_works(self):
        self.assertEqual([], list(self.l))

        called = []

        class X:
            def y(self, arg):
                called.append(arg)

        x = X()

        self.l.append(x.y)

        for fn in self.l:
            fn("arg")
            self.assertEqual(["arg"], called)
            del fn # fn holds the reference; so delete it.

        del x

        self.assertEqual([], list(self.l))





class WeakListTestCase(unittest.TestCase):

    def setUp(self):
        self.l = ut.WeakCollection()


    def test_init(self):
        self.assertFalse(self.l)
        self.assertEqual(len(self.l), 0)
        l = ut.WeakCollection([self.l])
        self.assertEqual(len(l), 1)
        self.assertEqual(list(l), [self.l])


    def test_append_remove(self):
        def m1():
            pass
        def m2():
            pass
        def m3():
            pass

        self.assertEqual(len(self.l), 0)

        self.l.append(m1, m2)
        self.assertEqual(len(self.l), 2)

        self.l.append(m2, m2) # dupes
        self.assertEqual(len(self.l), 4)

        # No error on missing
        self.l.remove(m3)
        self.l.removeAll(m3)
        self.assertEqual(len(self.l), 4)

        self.l.remove(m2)
        self.assertEqual(len(self.l), 3)

        # No error on missing
        self.l.removeAll(m2)
        self.assertEqual(len(self.l), 1)

        del m1

        # It's still weak
        self.assertEqual(len(self.l), 0)



class AbstractPriorityDictionaryTestCase(unittest.TestCase):

    class SampleAbstractPriorityDictionary(ut.AbstractPriorityDictionary):
        def __init__(self, test):
            super(
                AbstractPriorityDictionaryTestCase.SampleAbstractPriorityDictionary,
                self).__init__()
            self.test = test

        def _ordered_configs(self):
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
        self.assertListEqual(obj._ordered_configs(), dict_list)
