__author__ = 'Lee Symes'


from twisted.internet import reactor, task
from twisted.internet.protocol import Factory
from twisted.protocols.amp import AMP

from lib import general_commands
from lib.commands import ConfiguredCommandAMP
from lib.file_helper import load_json
from lib.monitor import FilteredFilesInFolderMonitor
from lib.manager import get_queue_directories
from lib.manager.queue import EncoderQueue


# Load the config as a dictionary from the JSON file.
manager_config = load_json("manager.json")
print manager_config

#
registered_stations = {}
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


class DeadStationRemoverAMP(ConfiguredCommandAMP):
    """
    This class monitors connection and disconnection

    """

    def startReceivingBoxes(self, boxSender):
        """
        self.transport.client -> tuple(ip_address, port)
        """
        print boxSender
        registered_stations[self.transport.client] = StationInformation(boxSender)
        ConfiguredCommandAMP.startReceivingBoxes(self, boxSender)

    def sendBox(self, box):
        print "Sending:  ", box
        super(DeadStationRemoverAMP, self).sendBox(box)

    def ampBoxReceived(self, box):
        print "Received: ", box
        super(DeadStationRemoverAMP, self).ampBoxReceived(box)

    def stopReceivingBoxes(self, reason):
        """
        No further boxes will be received on this connection.

        @type reason: L{Failure}
        """
        # The transport.client will give a unique tuple which we can link up to a registered station and then remove
        # because it's disconnecting.
        client = self.transport.client
        print "Disconnecting from     ", client
        print "Discarded Information: ", registered_stations.pop(client, "NO INFORMATION STORED")
        registered_stations.pop(client, {})
        ConfiguredCommandAMP.stopReceivingBoxes(self, reason)


@general_commands.manager_commands.responder(general_commands.RegisterStationCommand)
def register_station(config, transport):
    client = transport.client
    if client not in registered_stations:
        registered_stations[client] = StationInformation(transport)
    info = registered_stations[client]

    info.station_config = config

    role_config = {"encode":
                       {"uuid": "encode",
                        "command": "echo"
                       }}

    info.station_config.roles = role_config

    return {"config": role_config}


def configure_encoder_fs_watch():
    if "encode" not in manager_config["queues"]:
        print "Inside check failed. ", manager_config["queues"].iterkeys()
        # No configuration for encoding.
        return
    encode_config = manager_config["queues"]["encode"]
    base_path = encode_config["base_path"]
    todo_path = get_queue_directories(base_path, "todo")
    encode_queue = EncoderQueue(encode_config, registered_stations)

    l = task.LoopingCall(FilteredFilesInFolderMonitor(todo_path,
                                                      encode_config["file_pattern"],
                                                      encode_queue))
    l.start(10.0, now=True) # Call every minute. Wait a minute before starting.












def create_and_configure_AMP():
    print "Configure"
    amp = DeadStationRemoverAMP()
    return amp


def main():
    general_commands.manager_commands.register()
    # FROM: http://twistedmatrix.com/documents/current/core/examples/ampserver.py

    pf = Factory()
    pf.noisy = True
    pf.protocol = create_and_configure_AMP

    configure_encoder_fs_watch()

    reactor.listenTCP(manager_config["listen_port"], pf)
    reactor.run()

if __name__ == "__main__":
    main()



