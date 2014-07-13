# FROM: http://twistedmatrix.com/documents/current/_downloads/ampclient.py
import json_helper
import os
from twisted.internet import reactor, task
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.protocols.amp import AMP

from roles.encode import MessagingCommand
from lib.json_helper import load_json

# Load the config as a dictionary from the JSON file.
station_config = load_json("station.json")

manager_endpoint = TCP4ClientEndpoint(reactor, station_config["manager_address"], station_config["manager_port"])


def doMath():
    sumDeferred = connectProtocol(manager_endpoint, AMP())
    def connected(ampProto):
        print repr(ampProto)
        r = ampProto.callRemote(MessagingCommand, msg="Hello World", time=1024)
        print "c -", repr(r)
        return r
    sumDeferred.addCallback(connected)
    def summed(result):
        print repr(result)
        r = result['resp']
        print "s -", repr(r)
        return r
    sumDeferred.addCallback(summed)


def doLooping():
    pass

def doRun():
    doMath()
    doLooping()
    reactor.run()

doRun()
