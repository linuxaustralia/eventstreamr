__author__ = 'Lee Symes'

from datetime import time, datetime

from twisted.application.service import Service
from twisted.internet import protocol, reactor

from lib.amp.mixins import CommandRegistrationServiceMixin
from lib.amp import arguments as amp
from lib.commands import configuration_helper
from lib.file_helper import object_to_json_string
from roles import RoleFactory, Role, register_factory
from lib.computer_info import load_averages, num_cores
from lib.logging import getLogger

log = getLogger(("encode", "general"))

_encode_job_station = configuration_helper("encode jobs(On Station)")
encode_job_manager = configuration_helper("encode jobs(On Manager)")


@_encode_job_station.command
class StartEncodeRequest(amp.Command):
    arguments = [('sender', amp.BoxSender()),
                 ('job_uuid', amp.String()),
                 ('job_config', amp.Object())]
    response = [('accepted', amp.Boolean())]


@encode_job_manager.command
class EncodeCompleted(amp.Command):
    arguments = [('uuid', amp.String())]
    response = []


@encode_job_manager.command
class EncodeFailed(amp.Command):
    arguments = [('uuid', amp.String()),
                 ('reason', amp.Object())]
    response = []


class EncodeRole(CommandRegistrationServiceMixin, Role):

    def __init__(self):
        Role.__init__(self)
        CommandRegistrationServiceMixin.__init__(self,
                                                 _encode_job_station,
                                                 (StartEncodeRequest, self.start_encode))
        self.config = {}
        log.msg("EncodeRole 123")

    def start_encode(self, sender, job_uuid, job_config):
        if not self.can_encode():
            return {"accepted": False}
        # Add more in here(if too many may move into a separate function).
        EncodeRunner(sender, job_uuid, self.config, job_config).setServiceParent(self)
        return {"accepted": True}

    def can_encode(self):
        if self.config.get("is_mixer", False):
            if time(7) <= datetime.now().time() <= time(19):
                # Between 7am and 7pm on a mixer so we won't do any encoding.
                return False
        if load_averages()[1] > 0.8: # Load for the past 5 minutes averaging more than 80%
            log.msg("5 Minute Average Load too damn high")
            return False
        if load_averages()[0] > 0.9: # Load for the past 1 minute averaging more than 90%.
            log.msg("1 Minute Average Load too damn high")
            return False
        if len(self.services) >= num_cores(): # One job per core.
            log.msg("I've got a lot on my plate right now. I only have so many CPUs.")
            return False
        return True

    def update(self, config):
        self.config = config


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


class EncodeRunner(Service, protocol.ProcessProtocol):

    def __init__(self, sender, uuid, base_config, job_config):
        self.sender = sender
        self.uuid = uuid
        self.base_config = base_config
        self.job_config = job_config
        self.log = getLogger(("encode", uuid))
        print self.log
        self.log.msg("Starting %r with %r" % (uuid, job_config))

    def startService(self):
        # Modify this to change what arguments are passed in. Currently it's just the json of the config, but you may
        # want/need the UUID as well. It's up to you.
        command = [self.base_config["script"]] + [object_to_json_string(self.job_config)]
        self.log.msg("Command to be run: %r" % command)
        reactor.spawnProcess(self, command[0], command)
        Service.startService(self)

    def connectionMade(self):
        self.log.msg("%r has started." % self.uuid)
        self.transport.closeStdin()

    def outReceived(self, data):
        self.log.msg("\n".join(["OUT | " + line for line in data.splitlines()]))

    def errReceived(self, data):
        self.log.msg("\n".join(["ERR | " + line for line in data.splitlines()]))

    def processEnded(self, reason):
        self.disownServiceParent()
        self.log.msg("%r has ended with the following reason: %r." % (self.uuid, reason.value))
        if reason.value.exitCode == 0:
            self.sender.callRemote(EncodeCompleted, uuid=self.uuid)
        else:
            self.sender.callRemote(EncodeFailed,
                                   uuid=self.uuid,
                                   reason={"exitCode": reason.value.exitCode,
                                           "signal": reason.value.signal})
