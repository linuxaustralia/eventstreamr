__author__ = 'lee'

from twisted.internet import protocol, reactor


class CommandRegistrationServiceMixin(object):

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


class PollingServiceMixin(object):

    def __init__(self, poll_length=None):
        if poll_length is not None:
            self.poll_length = poll_length
        self.call_later = None

    def do_poll(self):
        pass

    def startService(self):
        def __do_poll():
            self.call_later = reactor.callLater(self.poll_length, __do_poll)
            self.do_poll()
        self.call_later = reactor.callLater(self.poll_length, __do_poll)

    def stopService(self):
        if self.call_later and self.call_later.active():
            self.call_later.cancel()


class PollingCommandServiceMixin(PollingServiceMixin):

    def __init__(self, poll_length=None, command=None):
        if command is not None:
            self.command = lambda: command
        PollingServiceMixin.__init__(self, poll_length)

    def do_poll(self):
        command = [str(c) for c in self.command()]
        reactor.spawnProcess(PollingCommandServiceMixin._ProcessProtocol(self), command[0], command)

    def startService(self):
        self.call_later = reactor.callLater(self.poll_length, self.do_poll)

    def connection_made(self, transport):
        pass

    def out_received(self, data):
        pass

    def err_received(self, data):
        pass

    def process_ended(self, reason):
        pass

    def command(self):
        pass

    class _ProcessProtocol(protocol.ProcessProtocol):

        def __init__(self, command_service):
            """

            :param command_service:
            :type command_service: PollingCommandServiceMixin
            :return:
            :rtype:
            """
            self.command_service = command_service

        def connectionMade(self):
            try:
                self.command_service.connection_made(self.transport)
            finally:
                self.transport.closeStdin()

        def outReceived(self, data):
            self.command_service.out_received(data)

        def errReceived(self, data):
            self.command_service.err_received(data)

        def processEnded(self, reason):
            self.command_service.call_later = reactor.callLater(self.command_service.poll_length,
                                                                self.command_service.do_poll)
            self.command_service.process_ended(reason)
