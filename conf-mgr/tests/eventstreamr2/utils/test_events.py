import unittest

import eventstreamr2.utils.events as ut

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

    def test_weak_reference_acts_correctly(self):
        called = []
        def callee():
            called.append("")
        self.obj.add_weak_observer(callee)
        self.obj._notify_observers()
        self.assertEqual(1, len(called))
        del callee

        self.obj._notify_observers()
        self.assertEqual(1, len(called))

    def callee_for_testing(self, array):
        array.append("")

    def test_weak_reference_acts_correctly_with_bound_handler(self):
        called = []
        class X:
            def callee(self):
                called.append("")

        x1 = X()
        x2 = X()

        self.obj.add_weak_observer(x1.callee)
        self.obj.add_observer(x2.callee)
        self.obj._notify_observers()
        self.assertEqual(2, len(called))
        called[:] = [] # Empty

        del x1

        self.obj._notify_observers()
        self.assertEqual(1, len(called))
