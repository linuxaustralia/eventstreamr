"""
This module provides additional argument types.

This also provides all the existing argument types provided by twisted.
"""

import pickle as _pickle
from StringIO import StringIO as _StringIO
from itertools import count as _count

from twisted.protocols.amp import Argument as _Argument
# Allow items to just import this file and have access to all of the argument types.
from twisted.protocols.amp import Integer, Float, Boolean, Unicode, Path, Command, String

CHUNK_MAX = 0xffff


class Transport(_Argument, object):
    """
    An AMP argument that provides the :code:`transport` object to the reciever.

    The parameter does not need to be specified when called as it has no meaning to the sender.
    """


    def __init__(self):
        super(Transport, self).__init__(optional=True)


    def fromBox(self, name, strings, objects, proto):
        """
        Populates the argument with the :code:`transport`.
        """
        objects[name] = proto.transport  # The object will be filled in here


    def toBox(self, name, strings, objects, proto):
        """
        Ignore any argument given and transmit an empty string.
        """
        strings[name] = ""  # The object will be filled in on the other end.



class BoxSender(_Argument):
    """
    An AMP argument that provides the :code:`boxSender` object to the reciever.

    The parameter does not need to be specified when called as it has no meaning to the sender.
    """


    def __init__(self):
        _Argument.__init__(self, optional=True)


    def fromBox(self, name, strings, objects, proto):
        """
        Populates the argument with the :code:`boxSender`.
        """
        objects[name] = proto.boxSender  # The object will be filled in here


    def toBox(self, name, strings, objects, proto):
        """
        Ignore any argument given and transmit an empty string.
        """
        strings[name] = ""  # The object will be filled in on the other end.



class BigString(_Argument):
    """
    Encodes an arbitrarily large string for transmission.

    This is taken from http://amp-protocol.net/Types/BigString/
    """


    def fromBox(self, name, strings, objects, proto):
        value = _StringIO()
        value.write(strings.get(name))
        for counter in _count(2):
            chunk = strings.get("%s.%d" % (name, counter))
            if chunk is None:
                break
            value.write(chunk)
        objects[name] = self.build_value(value.getvalue())


    def build_value(self, value):
        """
        Converts the recieved string to another type if required.
        """
        return value


    def toBox(self, name, strings, objects, proto):
        value = _StringIO(self.from_value(objects[name]))
        first_chunk = value.read(CHUNK_MAX)
        strings[name] = first_chunk
        counter = 2
        while True:
            next_chunk = value.read(CHUNK_MAX)
            if not next_chunk:
                break
            strings["%s.%d" % (name, counter)] = next_chunk
            counter += 1


    def from_value(self, value):
        """
        Converts the value to be sent to a string for transmission.
        """
        return value



class BigUnicode(BigString):
    """
    Encodes an arbitrarily large unicode string for transmission over the network.
    """


    def build_value(self, value):
        return value.decode('utf-8')


    def from_value(self, value):
        return value.encode('utf-8')



class Object(BigUnicode):
    """
    An Argument that allows the sending of most python objects.

    This uses L{pickle} to convert the object from the sender to a string, then the reciever
    converts the string back to an object.
    """


    def build_value(self, value):
        return _pickle.loads(BigUnicode.build_value(self, value))


    def from_value(self, value):
        return BigUnicode.from_value(self, _pickle.dumps(value))



__all__ = ["BigString", "BigUnicode", "Boolean", "BoxSender", "Command", "Float", "Integer",
            "Object", "Path", "String", "Transport", "Unicode"]
