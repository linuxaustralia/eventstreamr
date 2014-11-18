__author__ = 'Lee Symes'

import pickle as _pickle
from StringIO import StringIO as _StringIO
from itertools import count as _count

from twisted.protocols.amp import Argument as _Argument
# Allow items to just import this file and have access to all of the argument types.
from twisted.protocols.amp import Integer, Float, Boolean, Unicode, Path, Command, String

CHUNK_MAX = 0xffff


class Transport(_Argument):
    optional = True  # No need to put this as an argument when calling.

    def __init__(self):
        _Argument.__init__(self, optional=True)

    def fromBox(self, name, strings, objects, proto):
        objects[name] = proto.transport  # The object will be filled in here

    def toBox(self, name, strings, objects, proto):
        strings[name] = ""  # The object will be filled in on the other end.


class BoxSender(_Argument):
    optional = True  # No need to put this as an argument when calling.

    def __init__(self):
        _Argument.__init__(self, optional=True)

    def fromBox(self, name, strings, objects, proto):
        objects[name] = proto.boxSender  # The object will be filled in here

    def toBox(self, name, strings, objects, proto):
        strings[name] = ""  # The object will be filled in on the other end.


class BigString(_Argument):
    """
    Encodes an arbitrarily large chunk of data by dynamically adding key/value
    pairs to the AMP Command packet. This is not a standard encoding scheme.

    This is little more than a hack, and services no purpose save convenience
    for some simple applications.

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
        return value


class BigUnicode(BigString):
    """
    Encodes an arbitrarily large chunk of data by dynamically adding key/value
    pairs to the AMP Command packet. This is not a standard encoding scheme.

    This is little more than a hack, and services no purpose save convenience
    for some simple applications.

    This is taken from http://amp-protocol.net/Types/BigString/
    """
    def build_value(self, value):
        return value.decode('utf-8')

    def from_value(self, value):
        return value.encode('utf-8')


class Object(BigUnicode):

    def build_value(self, value):
        return _pickle.loads(BigUnicode.build_value(self, value))

    def from_value(self, value):
        return BigUnicode.from_value(self, _pickle.dumps(value))

__all__ = ["BigString", "BigUnicode", "Boolean", "BoxSender", "Command", "Float", "Integer", "Object", "Path",
           "String", "Transport", "Unicode"]