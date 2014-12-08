"""
Common sub-services such as executing a program every n seconds.
"""

from lib.amp.mixins import InternalServiceMixin
from twisted.application.service import Service
from twisted.internet.defer import Deferred
from twisted.internet import protocol


class DefaultProcessProtocol(protocol.ProcessProtocol):


    def __init__(self):
        pass


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
        self.command_service.call_later
        self.command_service.process_ended(reason)



class _InternalProcessProtocol(protocol.ProcessProtocol):


    def __init__(self, run_after_exit, child_protocol):
        self.callback = run_after_exit
        self.child = child_protocol


    def makeConnection(self, process):
        if self.child.makeConnection:
            self.child.makeConnection(process)


    def childDataReceived(self, childFD, data):
        if self.child.childDataReceived:
            self.child.childDataReceived(childFD, data)


    def childConnectionLost(self, childFD):
        if self.child.childConnectionLost:
            self.child.childConnectionLost(childFD)


    def processExited(self, reason):
        if self.child.processExited:
            self.child.processExited(reason)


    def processEnded(self, reason):
        self.callback()
        if self.child.processEnded:
            self.child.processEnded(reason)



class ProgramExecutionService(InternalServiceMixin, Service):
    """



    """


    def __init__(self, program_exec, time_between_exec=0,
                        protocol=DefaultProcessProtocol, **kwargs):
        super(ProgramExecutionService, self).__init__(**kwargs)
        self.program_exec = program_exec
        self.delay = time_between_exec
        self.protocol = protocol
        self.started = False
        self.stopDeferred = None
        self.process = None


    def startService(self):
        super(ProgramExecutionService, self).startService()
        self.started = True
        self._run_process()


    def stopService(self):
        super(ProgramExecutionService, self).stopService()
        self.started = False
        if self.process and self.process.pid:
            self.stopDeferred = Deferred()
            def cb(arg):
                self.stopDeferred = None
            self.stopDeferred.addBoth(cb)
            try:
                self.process.signalProcess("TERM")
            except ProcessExitedAlready:
                pass # No op(prevent race condition causing problem)
            return self.stopDeferred


    def _run_process(self):
        if self.stopDeferred is not None:
            self.stopDeferred.callback(True)
            return # Shutting down. So we fire the callback when the process has terminated.
                    # We won't need to do any more processing so return.
        if not self.started:
            return # Service not running, so don't start the process
        if self.process and self.process.pid:
            return # Existing process still running.

        protocol = _InternalProcessProtocol(_run_process, self.protocol())
        if self.delay > 0:
            self.reactor.callLater(_spawn_process, self.delay, protocol)
        else:
            _spawn_process(protocol)


    def _spawn_process(self, protocol):
        self.process = self.reactor.spawnProcess(protocol, self.command[0], self.command);
