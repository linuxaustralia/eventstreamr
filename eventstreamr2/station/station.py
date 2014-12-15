#!/usr/bin/python
__author__ = "Lee Symes"

from twisted.application import internet
from twisted.application.service import Application, MultiService
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ReconnectingClientFactory

from eventstreamr2.lib.commands import ListenableConfiguredAMP
from eventstreamr2.lib.general_commands import RegisterStationCommand
from eventstreamr2.lib.file_helper import load_json, save_json, isfile
from eventstreamr2.lib.config import StationConfig, ConfigurationManagerService
from eventstreamr2.lib.logging import transmit_service, getLogger

log = getLogger(("general", ))

class StationClientFactory(ReconnectingClientFactory):
    maxDelay = 5
    initialDelay = 1

    def __init__(self):
        pass
        # When the protocol is started, reset the delay in here.

    def buildProtocol(self, address):
        return ListenableConfiguredAMP(start=self.connected)

    def connected(self, amp, box_sender):
        self.resetDelay()
        register_station(box_sender)
        transmit_service.remote_connection = box_sender

    def clientConnectionLost(self, connector, unused_reason):
        transmit_service.remote_connection = None
        ReconnectingClientFactory.clientConnectionLost(self, connector, unused_reason)

    def clientConnectionFailed(self, connector, reason):
        transmit_service.remote_connection = None
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


@inlineCallbacks
def register_station(connection):
    log.msg("Attempting to register station and update configs.")
    #print repr(connection)

    # Make the manager send the configs as a new command to allow us to send errors back.
    # Station still sends existing config on the 'hello' command.
    try:
        yield connection.callRemote(RegisterStationCommand, config=role_config)
    except:
        log.error("Failed to call remote manager to say hello")

    log.msg("New Config:" + repr(role_config))


def load_role_config():
    config = StationConfig(blocked_roles=static_config["blocked_roles"])
    if isfile(static_config["dynamic_config"]):
        config.roles = load_json(static_config["dynamic_config"])
    return config


def save_role_config(roles):
    save_json(roles, static_config["dynamic_config"])

static_config = load_json("station.json")

role_config = load_role_config()

service_wrapper = MultiService()

configuration_manager_service = ConfigurationManagerService(role_config, update_callback=save_role_config)
configuration_manager_service.setServiceParent(service_wrapper)

transmit_service.setServiceParent(service_wrapper)

client = internet.TCPClient(static_config["manager_address"], static_config["manager_port"], StationClientFactory())
client.setServiceParent(service_wrapper)

application = Application("EventStreamr Station")
service_wrapper.setServiceParent(application)

if __name__ == "__main__":
    print "Please run this file using the following command - It makes life easier."
    print "\ttwistd --pidfile station.pid --nodaemon --python station.py"
