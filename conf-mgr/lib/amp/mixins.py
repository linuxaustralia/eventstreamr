"""
This module provides some basic mixin classes to be used when implementing Twisted services.
"""


from twisted.internet import protocol, reactor


class InternalServiceMixin(object):
    """
    A base class that provides easier implementation of sub-services. It automatically initilises
    the configuration manager and reactor passed in.

    To use simple extend this class and define your init method as shown::

        def __init__(self, ..., **kwargs):
            super(..., self).__init__(self, **kwargs)
            ...

    :ivar _config_mgr: A configuration manager instance which contains all the configurations.
    :type _config_mgr: :class:`ConfigurationManager <lib.configuration.ConfigurationManager>`
    :ivar _reactor: A twisted reactor instance to be used for this service. Use this over importing
                    :code:`twisted.internet.reactor` as it allows for easier testing.
    """


    def __init__(self, *args, **kwargs):
        """
        This method initilises the service with the configuration manager and reactor passed in as
        keyword args.

        :param _config_mgr: The configuration manager for this service(KW args only)
        :param _reactor: The reactor for this service(KW args only)
        """
        self._config_mgr = kwargs["_config_mgr"]
        self._reactor = kwargs["_reactor"]
        super(ConfMgrService, self).__init__(self, *args, **kwargs)


    def _init_new_service(self, service_class, *args, **kwargs):
        """
        Create a new service using this service's configuration manager and reactor. Additional
        parameters after the :code:`service_class` will be passed through to the class's
        constructor.

        :param service_class: The service class to create.
        :param \*args: The positional arguments to send to the service class's constructor.
        :param \*\*kwargs: The keyword arguments to send to the service class's constructor. Note
                         that :code:`_config_mgr` and :code:`_reactor` are always overwritten.
        """
        kwargs["_config_mgr"] = _config_mgr
        kwargs["_reactor"] = _reactor
        return service_class(*args, **kwargs)



class CommandRegistrationServiceMixin(object):
    """
    """


    def __init__(self, helper, *command_responder_pairs):
        """

        :param helper:
        :type helper: lib.commands._ConfigurationHelper
        :param command_responder_pairs:
        :type command_responder_pairs:
        :return:
        :rtype:
        """
        self.__helper = helper
        self.__command_pairs = command_responder_pairs


    def startService(self):
        for command, responder in self.__command_pairs:
            self.__helper.responder(command, responder)
        self.__helper.register()

        super(CommandRegistrationServiceMixin, self).startService()


    def stopService(self):
        for command, responder in self.__command_pairs:
            self.__helper.remove_responder(command, responder)

        super(CommandRegistrationServiceMixin, self).stopService()


# TODO rework the polling.
# class PollingServiceMixin(object):
#     """
#     """
#
#
#     def __init__(self, poll_length=None):
#         if poll_length is not None:
#             self.poll_length = poll_length
#         self.call_later = None
#
#
#     def do_poll(self):
#         pass
#
#
#     def startService(self):
#         def __do_poll():
#             self.call_later = reactor.callLater(self.poll_length, __do_poll)
#             self.do_poll()
#         self.call_later = reactor.callLater(self.poll_length, __do_poll)
#
#
#     def stopService(self):
#         if self.call_later and self.call_later.active():
#             self.call_later.cancel()
#         self.call_later = None
#
#
#
# class PollingCommandServiceMixin(PollingServiceMixin):
#     """
#     """
#
#
#     def __init__(self, poll_length=None, command=None):
#         if command is not None:
#             if callable(command):
#                 self.command = command
#             else:
#                 self.command = lambda: command
#         PollingServiceMixin.__init__(self, poll_length)
#
#
#     def do_poll(self):
#         try:
#             command = [str(c) for c in self.command()]
#         except:
#             self.do_call_later()
#             print "Error occured. Trying again later"
#             return
#         print "Running %r" % command
#         reactor.spawnProcess(PollingCommandServiceMixin._ProcessProtocol(self), command[0], command)
#
#
#     def do_call_later(self, override=True):
#         if (override and self.call_later is None) or (self.call_later is not None):
#             self.call_later = reactor.callLater(self.poll_length,
#                                               self.do_poll)
#
#
#     def startService(self):
#         self.do_call_later(override=False)
#
#
#     def connection_made(self, transport):
#         pass
#
#
#     def out_received(self, data):
#         pass
#
#
#     def err_received(self, data):
#         pass
#
#
#     def process_ended(self, reason):
#         pass
#
#
#     def command(self):
#         pass
#
#
#     class _ProcessProtocol(protocol.ProcessProtocol):
#
#
#         def __init__(self, command_service):
#             """
#
#             :param command_service:
#             :type command_service: PollingCommandServiceMixin
#             :return:
#             :rtype:
#             """
#             self.command_service = command_service
#
#
#         def connectionMade(self):
#             try:
#                 self.command_service.connection_made(self.transport)
#             finally:
#                 self.transport.closeStdin()
#
#
#         def outReceived(self, data):
#             self.command_service.out_received(data)
#
#
#         def errReceived(self, data):
#             self.command_service.err_received(data)
#
#
#         def processEnded(self, reason):
#             self.command_service.call_later
#             self.command_service.process_ended(reason)
