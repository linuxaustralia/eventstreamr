__author__ = 'Lee Symes'


from twisted.internet import protocol
from twisted.internet import reactor
from twisted.python import log

from lib.amp import arguments as amp
from lib.commands import configuration_helper
from lib.file_helper import object_to_json_string
from roles import RoleFactory, Role, register_factory

_encode_job_station = configuration_helper("encode jobs(On Station)")
encode_job_manager = configuration_helper("encode jobs(On Manager)")


@_encode_job_station.command
class StartEncodeRequest(amp.Command):
    arguments = [('sender', amp.BoxSender()),
                 ('job_uuid', amp.Unicode()),
                 ('job_config', amp.Object())]
    response = [('accepted', amp.Boolean())]


@encode_job_manager.command
class EncodeCompleted(amp.Command):
    arguments = [('uuid', amp.Unicode())]
    response = []


@encode_job_manager.command
class EncodeFailed(amp.Command):
    arguments = [('uuid', amp.Unicode()),
                 ('reason', amp.Object())]
    response = []


class EncodeRole(Role):
# These should probably be services that are started and stopped. I think
# http://krondo.com/wp-content/uploads/2009/08/twisted-intro.html#post-2345
# This also mentions how to initilise twisted as a daemon.

    def __init__(self):
        super(EncodeRole, self).__init__()
        self.config = {}

    def start_encode(self, sender, job_uuid, job_config):
        EncodeRunner(sender, job_uuid, self.config, job_config).start()
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

    def __init__(self, sender, uuid, base_config, job_config):
        self.sender = sender
        self.uuid = uuid
        self.base_config = base_config
        self.job_config = job_config

    def start(self):
        # Modify this to change what arguments are passed in. Currently it's just the json of the config, but you may
        # want/need the UUID as well. It's up to you.
        command = [self.base_config["script"]] + [object_to_json_string(self.job_config)]
        log.msg("Command to be run: %r" % command)
        pp = EncodeProcessProtocol(self.sender, self.uuid)
        reactor.spawnProcess(pp, command[0], command)


class EncodeProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, sender, uuid):
        self.sender = sender
        self.uuid = uuid

    def connectionMade(self):
        log.msg("%r has started." % self.uuid)
        self.transport.closeStdin()

    def outReceived(self, data):
        log.msg("\n".join(["OUT | " + line for line in data.splitlines()]))

    def errReceived(self, data):
        log.msg("\n".join(["ERR | " + line for line in data.splitlines()]))

    def processEnded(self, reason):
        log.msg("%r has ended with the following reason: %r." % (self.uuid, reason.value))
        if reason.value.exitCode == 0:
            self.sender.callRemote(EncodeCompleted, uuid=self.uuid)
        else:
            self.sender.callRemote(EncodeFailed,
                                   uuid=self.uuid,
                                   reason={"exitCode": reason.value.exitCode,
                                           "signal": reason.value.signal})