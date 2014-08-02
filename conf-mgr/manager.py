__author__ = 'Lee Symes'

from lib.logging import getLogger
print "Manager Imported!!!!"
transmit = False  # First thing is don't transmit.

from twisted.application.service import Application, MultiService, Service
from twisted.application import internet
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.protocol import ServerFactory
from twisted.protocols.amp import AMP

from lib import general_commands
from lib.commands import ListenableConfiguredAMP
from lib.config import UpdateConfiguration
from lib.exceptions import InvalidConfigurationException
from lib.file_helper import load_json
import lib.manager.queue
from lib.manager.config_manager import StationConfigManager
from lib.manager.station_logs import StationLogReceiver



log = getLogger(("manager", ), False)

_registered_stations = {}
"""
A Dictionary mapping between the ip/port tuple and the station's config. This will never contain empty values.
Once a station disconnects it's information is removed from this dictionary.

:type : dict[tuple[string,int],StationInformation]
"""


class StationInformation:
    def __init__(self, station_transport, station_config=None):
        """

        :type station_transport: AMP
        :type station_config: lib.config.StationConfig
        """
        self.station_transport = station_transport
        self.station_config = station_config

    def __str__(self):
        return "%s -> %s" % (self.station_transport, self.station_config)

    @property
    def name(self):
        return "%s(%s|%s)" % (self.station_config.hostname, self.station_config.ip, self.station_config.mac_address)

    @property
    def mac(self):
        return self.station_config.mac_address

    @property
    def roles(self):
        if self.station_config:
            return self.station_config.roles
        return {}


class ManagerServerFactory(ServerFactory):
    maxDelay = 30
    initialDelay = 5

    def __init__(self):
        pass

    def protocol(self):
        return ListenableConfiguredAMP(start=self.connected, stop=self.disconnected)

    def disconnected(self, amp, reason):
        """
        No further boxes will be received on this connection.

        @type reason: L{Failure}
        """
        # The transport.client will give a unique tuple which we can link up to a registered station and then remove
        # because it's disconnecting.
        client = amp.transport.client
        log.msg("Disconnecting from     %r" % (client, ))
        log.msg("Discarded Information: %r" % (_registered_stations.pop(client, "NO INFORMATION STORED"), ))
        _registered_stations.pop(amp.transport.client, {})

    def connected(self, amp, box_sender):
        """
        self.transport.client -> tuple(ip_address, port)
        """
        log.msg("Connected to %r -> %r" % (amp.transport.client, box_sender))
        _registered_stations[amp.transport.client] = StationInformation(box_sender)


class RegisterStationWithManagerService(Service):

    def __init__(self):
        self.setName("Register Station With Manager Service")

    def startService(self):
        general_commands.manager_commands.responder(general_commands.RegisterStationCommand)(self.register_station)
        general_commands.manager_commands.register()

    def stopService(self):
        general_commands.manager_commands.de_register()
        general_commands.manager_commands.remove_responder(general_commands.RegisterStationCommand,
                                                           self.register_station)
        pass

    @inlineCallbacks
    def register_station(self, config, transport, box_sender):
        client = transport.client
        if client not in _registered_stations:
            _registered_stations[client] = StationInformation(transport)
        info = _registered_stations[client]

        info.station_config = config

        __ = """
            role_config = {
                            "role": {
                                "uuid": {
                                    "role": "encode",
                                    "timestamp": 1024
                                    ...
                                }
                                ...
                            },
                            "role2": {
                                "uuid": {
                                    "role": "dvswitch",
                                    "timestamp": 1025
                                    ...
                                }
                                ...
                            }
                          }

        """

        manager_role_config = config_manager.get_config_for(info.mac)

        # The manager's config takes priority in the event timestamps are missing in both.
        new_config = config_manager.merge_config(manager_role_config, config.roles)
        print "New Config: %r" % new_config
        config_manager.update_timestamps(new_config)
        try:
            yield box_sender.callRemote(UpdateConfiguration, roles=new_config)
            info.station_config.roles = new_config
            config_manager.set_config_for(info.mac, new_config)
        except InvalidConfigurationException:
            log.error("Failed to load config.")

        returnValue({})


class QueueManagerStation(MultiService):

    def __init__(self, queue_config):
        """

        :param queue_config:
        :type queue_config: dict(string, dict(string, object))
        :return:
        :rtype:
        """
        print queue_config
        MultiService.__init__(self)
        for queue_name, config in queue_config.iteritems():
            base_path = config["base_path"]
            poll_length = config.get("poll_length", 30)
            file_pattern = config.get("file_pattern", "*")
            station_config = config.get("station_config", {})
            queue = lib.manager.queue.create_queue(_registered_stations, queue_name, station_config,
                                                   base_path, file_pattern, poll_length)
            print "Started %r with %r: %r" % (queue_name, config, queue)
            queue.setServiceParent(self)

static_config = load_json("manager.json")

config_manager = StationConfigManager(static_config.get("config_storage", "station-config/"))

service_wrapper = MultiService()

server = internet.TCPServer(static_config["listen_port"], ManagerServerFactory())
server.setServiceParent(service_wrapper)

station_log_receiver = StationLogReceiver(_registered_stations)
station_log_receiver.setServiceParent(service_wrapper)

queue_manager = QueueManagerStation(static_config.get("queues", {}))
queue_manager.setServiceParent(service_wrapper)

station_register = RegisterStationWithManagerService()
station_register.setServiceParent(service_wrapper)

application = Application("EventStreamr Station")
service_wrapper.setServiceParent(application)

if __name__ == "__main__":
    print "Please run this file using the following command - It makes life easier."
    print "\ttwistd --pidfile manager.pid --nodaemon --python manager.py"



