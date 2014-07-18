__author__ = "Lee Symes"

import logging

from twisted.internet.protocol import ReconnectingClientFactory
from twisted.application import internet
from twisted.application.service import Application, MultiService
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

from lib.commands import ListenableConfiguredAMP
from lib.general_commands import RegisterStationCommand
from lib.file_helper import load_json, save_json, isfile
from lib.config import StationConfig, ConfigurationManagerService

log = logging.getLogger("station")
# Load the config as a dictionary from the JSON file.

class StationClientFactory(ReconnectingClientFactory):
    maxDelay = 30
    initialDelay = 5

    def __init__(self):
        self.amp = ListenableConfiguredAMP(start=self.connected)
        # When the protocol is started, reset the delay in here.

    def buildProtocol(self, address):
        return self.amp

    def connected(self, box_sender):
        self.resetDelay()
        register_station(box_sender)


def register_station(connection):
    print "Attempting to register station and update configs."
    if not connection:
        print "Called too early"
        return

    # Make the manager send the configs as a new command to allow us to send errors back.
    # Station still sends existing config on the 'hello' command.
    connection.callRemote(RegisterStationCommand, config=role_config)

    print "New Config:", repr(role_config)


def load_role_config():
    config = StationConfig(blocked_roles=static_config["blocked_roles"])
    if isfile(static_config["dynamic_config"]):
        config.roles = load_json(static_config["dynamic_config"])
    return config


def save_role_config(config):
    roles = config.roles
    save_json(roles, static_config["dynamic_config"])

static_config = load_json("station.json")

role_config = load_role_config()

service_wrapper = MultiService()

configuration_manager_service = ConfigurationManagerService(role_config, update_callback=save_role_config)
configuration_manager_service.setServiceParent(service_wrapper)

client = internet.TCPClient(static_config["manager_address"], static_config["manager_port"], StationClientFactory())
client.setServiceParent(service_wrapper)

application = Application("EventStreamr Station")
service_wrapper.setServiceParent(application)

if __name__ == "__main__":
    print "Please run this file using the following command - It makes life easier."
    print "\ttwistd --nodaemon --python station.py"