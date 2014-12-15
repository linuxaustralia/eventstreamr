import unittest
import eventstreamr2.lib.amp.service as srv

class __PrivateProcessProtocol(protocol.ProcessProtocol):


    def __init__(self, call_list):
        self.call_list = call_list


    def makeConnection(self, process):
        self.call_list.append(("makeConnection", process))


    def childDataReceived(self, childFD, data):
        self.call_list.append(("childDataReceived", childFD, data))


    def childConnectionLost(self, childFD):
        self.call_list.append(("childConnectionLost", childFD))


    def processExited(self, reason):
        self.call_list.append(("processExited", reason))


    def processEnded(self, reason):
        self.call_list.append(("processEnded", reason))


class Test_InternalProcessProtocol(unittest.TestCase):


    def setUp(self):
        def s():
            self.call_list.append(("callback", ))

        self.call_list = []
        self.child_proto = __PrivateProcessProtocol(self.call_list)
        self.proto = _InternalProcessProtocol(s, self.child_proto)


    def testCallsPassThrough(self):
        a1 = object()
        a2 = object()
        self.proto.makeConnection(a1)
        self.assertEqual(self.call_list.pop(0), ("makeConnection", a1))
        self.assertEqual(self.call_list, [])

        self.proto.childDataReceived(a1, a2)
        self.assertEqual(self.call_list.pop(0), ("childDataReceived", a1, a2))
        self.assertEqual(self.call_list, [])

        self.proto.childConnectionLost(a1)
        self.assertEqual(self.call_list.pop(0), ("childConnectionLost", a1))
        self.assertEqual(self.call_list, [])

        self.proto.processExited(a1)
        self.assertEqual(self.call_list.pop(0), ("processExited", a1))
        self.assertEqual(self.call_list, [])

        self.proto.processEnded(a1)
        self.assertEqual(self.call_list.pop(0), ("processEnded", a1))
        self.assertEqual(self.call_list.pop(0), ("callback",))
        self.assertEqual(self.call_list, [])
