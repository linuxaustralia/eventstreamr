import unittest
import lib.logging as _log

class _TmpObserver(_log.LogObserver):

    def __init__(self):
        pass

    def emmit(self, event):
        pass

    def print_to_sys(self, event):
        pass



class LoggingTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.old_observer = _log.observer
        cls.observer = _TmpObserver()
        _log.observer = cls.observer

    @classmethod
    def tearDownClass(cls):
        _log.observer = cls.old_observer
