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

_cut_job_station = configuration_helper("cut jobs(On Station)")
cut_job_manager = configuration_helper("cut jobs(On Manager)")


@_cut_job_station.command
class StartCutRequest(amp.Command):
    arguments = [('sender', amp.BoxSender()),
                 ('job_uuid', amp.String()),
                 ('job_config', amp.Object())]
    response = [('accepted', amp.Boolean())]


@cut_job_manager.command
class CutCompleted(amp.Command):
    arguments = [('uuid', amp.String())]
    response = []


@cut_job_manager.command
class CutFailed(amp.Command):
    arguments = [('uuid', amp.String()),
                 ('reason', amp.Object())]
    response = []


class CutRole(CommandRegistrationServiceMixin, Role):

    def __init__(self, uuid):
        self.log = getLogger(("cut", uuid))
        Role.__init__(self)
        CommandRegistrationServiceMixin.__init__(self,
                                                 _cut_job_station,
                                                 (StartCutRequest, self.start_cut))
        self.config = {}
        self.log.msg("CutRoles 123")

    def start_cut(self, sender, job_uuid, job_config):
        if not self.can_cut():
            return {"accepted": False}

        CutRunner(sender, job_uuid, self.config, job_config).setServiceParent(self)
        return {"accepted": True}

    def can_cut(self):
        # if load_averages()[1] > 0.8: # Load for the past 5 minutes averaging more than 80%
        #     self.log.msg("5 Minute Average Load too damn high")
        #     return False
        # if load_averages()[0] > 0.9: # Load for the past 1 minute averaging more than 90%.
        #     self.log.msg("1 Minute Average Load too damn high")
        #     return False
        # if len(self.services) >= num_cores(): # One job per core.
        #     self.log.msg("I've got a lot on my plate right now. I only have so many CPUs.")
        #     return False
        return True

    def update(self, config):
        self.config = config


########################################################################################################################
#                                   BEGIN ROLE FACTORY                                                                 #
########################################################################################################################


class CutRoleFactory(RoleFactory):

    instances = 1

    def __init__(self):
        super(CutRoleFactory, self).__init__()

    def build(self, uuid):
        return CutRole(uuid)


cut_factory = CutRoleFactory()


register_factory("cut", cut_factory)


########################################################################################################################
#                                   BEGIN ROLE CUT IMPLEMENTATION                                                   #
########################################################################################################################


class CutRunner(Service, protocol.ProcessProtocol):

    def __init__(self, sender, uuid, base_config, job_config):
        self.sender = sender
        self.uuid = uuid
        self.base_config = base_config
        self.job_config = job_config
        self.log = getLogger(("cut", uuid))
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
            self.sender.callRemote(CutCompleted, uuid=self.uuid)
        else:
            self.sender.callRemote(CutFailed,
                                   uuid=self.uuid,
                                   reason={"exitCode": reason.value.exitCode,
                                           "signal": reason.value.signal})
