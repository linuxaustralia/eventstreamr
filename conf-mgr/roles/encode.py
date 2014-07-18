__author__ = 'Lee Symes'


from twisted.internet import protocol
from twisted.internet import reactor

from lib.amp import arguments as amp
from lib.commands import configuration_helper
from roles import RoleFactory, Role, register_factory

_encode_job_station = configuration_helper("encode jobs(On Station)")
_encode_job_manager = configuration_helper("encode jobs(On Manager)")


@_encode_job_station.command
class StartEncodeRequest(amp.Command):
    arguments = [('transport', amp.BoxSender()),
                 ('job_uuid', amp.Unicode()),
                 ('input_files_and_cutoffs', amp.Object()),
                 ('output_file', amp.Unicode())]
    response = [('accepted', amp.Boolean())]


@_encode_job_manager.command
class EncodeCompleted(amp.Command):
    arguments = [('uuid', amp.Unicode())]
    response = []

@_encode_job_manager.command
class EncodeFailed(amp.Command):
    arguments = [('uuid', amp.Unicode()),
                 ('failure_information', amp.Object())]
    response = []


class EncodeRole(Role):
# These should probably be services that are started and stopped. I think
# http://krondo.com/wp-content/uploads/2009/08/twisted-intro.html#post-2345
# This also mentions how to initilise twisted as a daemon.

    def __init__(self):
        super(EncodeRole, self).__init__()
        self.config = {}

    def start_encode(self, sender, job_uuid, input_files_and_cutoffs, output_file):
        EncodeRunner(sender, job_uuid, self.config["command"], input_files_and_cutoffs, output_file).start()
        return {"accepted": True}

    def startService(self):
        _encode_job_station.responder(StartEncodeRequest)(self.start_encode)
        _encode_job_station.register()
        super(EncodeRole, self).startService()

    def update(self, config):
        self.config = config

    def stopService(self):
        # No longer responsible for encoding so de-list it as an option.
        _encode_job_station.remove_responder(StartEncodeRequest, self.start_encode)
        _encode_job_station.de_register()
        super(EncodeRole, self).stopService()


########################################################################################################################
#                                   BEGIN ROLE FACTORY                                                                 #
########################################################################################################################


class EncodeRoleFactory(RoleFactory):

    instances = 1

    def __init__(self):
        super(EncodeRoleFactory, self).__init__()

    def build(self):
        return EncodeRole()


encode_factory = EncodeRoleFactory()


register_factory("encode", encode_factory)


########################################################################################################################
#                                   BEGIN ROLE ENCODE IMPLEMENTATION                                                   #
########################################################################################################################


class EncodeRunner(object):

    def __init__(self, sender, uuid, command, input_files_and_cutoffs, output_file):
        self.sender = sender
        self.uuid = uuid
        self.command = command
        self.input_files_and_cutoffs = input_files_and_cutoffs
        self.output_file = output_file

    def start(self):
        pp = EncodeProcessProtocol(self.sender, self.uuid)
        # TODO spawn this process as a sub-service of the EncodeRole.
        reactor.spawnProcess(pp, self.command, (str(self.input_files_and_cutoffs), self.output_file))


class EncodeProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, sender, uuid, stdin="Hello World"):
        self.sender = sender
        self.uuid = uuid
        self.stdin = stdin

    def connectionMade(self):
        print "Connection Made"
        if self.stdin:
            self.transport.write(self.stdin)
        self.transport.closeStdin()

    def outReceived(self, data):
        print "\n".join(["OUT | " + line for line in data.splitlines()])

    def errReceived(self, data):
        print "\n".join(["ERR | " + line for line in data.splitlines()])

    def processEnded(self, reason):
        if reason.value.exitCode == 0:
            self.sender.callRemote(EncodeCompleted, uuid=self.uuid)
        else:
            self.sender.callRemote(EncodeFailed,
                                   uuid=self.uuid,
                                   failure_information={"exitCode": reason.value.exitCode,
                                                        "signal": reason.value.signal})











