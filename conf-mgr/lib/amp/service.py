"""
This module provides some basic mixin classes to be used when implementing Twisted services.
"""

# from lib.amp.mixins import PollingCommandServiceMixin
#
#
# class CommandWatchdogService(PollingCommandServiceMixin, Service, object):
#
#     def __init__(self, poll_length=0, command=None):
#         Service.__init__(self)
#         PollingCommandServiceMixin.__init__(self, poll_length, command)
#
#
#     def startService(self):
#         super(CommandWatchdogService, self).startService(self)
#
#
#     def stopService(self):
#         super(CommandWatchdogService, self).stopService(self)
#
#
#     def out_received(self, data):
#         try:
#             self.log.cmd_output_stdout(data)
#         except NameError:
#             pass
#
#
#     def err_received(self, data):
#         try:
#             self.log.cmd_output_stderr(data)
#         except NameError:
#             pass
