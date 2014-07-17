__author__ = 'Lee Symes'


from twisted.protocols import amp

from lib.amp import arguments as amp_args
from lib.commands import configuration_helper
from roles import RoleConfig, SingletonRoleFactory, SingletonRole

_encode_job_station = configuration_helper("encode jobs(On Station)")
_encode_job_manager = configuration_helper("encode jobs(On Manager)")

@_encode_job_station.command
class StartEncodeRequest(amp.Command):
    arguments = [('transport', amp_args.BoxSender()),
                 ('job_uuid', amp_args.Unicode()),
                 ('input_files_and_cutoffs', amp_args.Object()),
                 ('output_file', amp_args.Unicode())]
    response = [('accepted', amp_args.Boolean())]


@_encode_job_manager.command
class EncodeCompleted(amp.Command):
    arguments = [('uuid', amp_args.Unicode())]
    response = []

@_encode_job_manager.command
class EncodeFailed(amp.Command):
    arguments = [('uuid', amp_args.Unicode()),
                 ('failure_information', amp_args.Object())]
    response = []


class EncodeRoleConfig(RoleConfig):

    def __init__(self, in_dict):
        super(EncodeRoleConfig, self).__init__()
        self.command = in_dict["command"]

    def __dict__(self):
        return {"command": self.command}


class EncodeRole(SingletonRole):
# These should probably be services that are started and stopped. I think
# http://krondo.com/wp-content/uploads/2009/08/twisted-intro.html#post-2345
# This also mentions how to initilise twisted as a daemon.
    def __init__(self):
        super(SingletonRole, self).__init__()
        _encode_job_station.responder(StartEncodeRequest)(self.start_encode)
        _encode_job_station.register()
        print "Registered myself with the encode job."

    def start_encode(self, transport, job_uuid, input_files_and_cutoffs, output_file):
        print "Starting to encode job %s" % (job_uuid, )
        EncodeRunner(transport, job_uuid, self.config["command"], input_files_and_cutoffs, output_file).start()
        return {"accepted": True}

    def update(self, config):
        print "Updating configs: ", config
        self.config = config

    def stop(self):
        super(SingletonRole, self).stop()
        # No longer responsible for encoding so de-list it as an option.
        _encode_job_station.de_register()


########################################################################################################################
#                                   BEGIN ROLE FACTORY                                                                 #
########################################################################################################################


class EncodeRoleFactory(SingletonRoleFactory):

    def __init__(self):
        super(EncodeRoleFactory, self).__init__()

    def build_singleton(self):
        print "Building Singleton"
        return EncodeRole()


encode_factory = EncodeRoleFactory()

from roles import register_factory
register_factory("encode", encode_factory)


########################################################################################################################
#                                   BEGIN ROLE ENCODE IMPLEMENTATION                                                   #
########################################################################################################################

from twisted.internet import protocol
from twisted.internet.error import ProcessDone, ProcessTerminated
from twisted.internet import reactor


class EncodeRunner(object):

    def __init__(self, transport, uuid, command, input_files_and_cutoffs, output_file):
        self.transport = transport
        self.uuid = uuid
        self.command = command
        self.input_files_and_cutoffs = input_files_and_cutoffs
        self.output_file = output_file

    def start(self):
        pp = EncodeProcessProtocol(self.transport, self.uuid)
        reactor.spawnProcess(pp, self.command, (str(self.input_files_and_cutoffs), self.output_file))


class EncodeProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, transport, uuid, stdin="Hello World"):
        self._transport = transport
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
            self._transport.callRemote(EncodeCompleted, uuid=self.uuid)
        else:
            self._transport.callRemote(EncodeFailed,
                                       uuid=self.uuid,
                                       failure_information={"exitCode": reason.value.exitCode,
                                                            "signal": reason.value.signal})











