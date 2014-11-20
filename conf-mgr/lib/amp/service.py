__author__ = 'Lee Symes'

from lib.amp.mixins import PollingCommandServiceMixin
from twisted.application.service import Service

class CommandWatchdogService(PollingCommandServiceMixin, Service):

    __doc__

    def __init__(self, poll_length=0, command=None):
        Service.__init__(self)
        PollingCommandServiceMixin.__init__(self, poll_length, command)

    def startService(self):
        PollingCommandServiceMixin.startService(self)
        Service.startService(self)

    def stopService(self):
        PollingCommandServiceMixin.stopService(self)
        Service.stopService(self)

    def out_received(self, data):
        try:
            self.log.cmd_output_stdout(data)
        except NameError:
            pass

    def err_received(self, data):
        try:
            self.log.cmd_output_stderr(data)
        except NameError:
            pass