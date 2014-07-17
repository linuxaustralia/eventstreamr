from twisted.internet.main import CONNECTION_DONE

__author__ = "Lee Symes"


from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.error import ConnectError
from twisted.protocols.amp import AMP

from lib.commands import ConfiguredCommandAMP
from lib.general_commands import RegisterStationCommand
from lib.file_helper import load_json
from lib.config import StationConfig
import roles

# Load the config as a dictionary from the JSON file.
static_config = load_json("station.json")

role_config = StationConfig() # TODO load roles file.

executing_roles = {}
"""
:type dict(string, roles.Role)
"""

manager_endpoint = TCP4ClientEndpoint(reactor, static_config["manager_address"], static_config["manager_port"])

connection = None

@inlineCallbacks
def attempt_connection():
    print "Attempting to connect..."
    try:
        conn = yield connectProtocol(manager_endpoint, ConfiguredCommandAMP())
        global connection
        connection = conn
        yield register_station()
    except ConnectError:
        # Couldn't connect so try again in 30 seconds.
        print "Failed to connect so I'll try again in a few seconds"
        reactor.callLater(30, attempt_connection)
    update_executing_roles()


@inlineCallbacks
def register_station():
    print "Attempting to register station and update configs."
    if not connection:
        print "Called too early"
        return

    new_roles = yield connection.callRemote(RegisterStationCommand, config=role_config)
    role_config.roles = new_roles["config"]

    print "New Roles: ", repr(new_roles)
    print "New Config:", repr(role_config)


def update_executing_roles():
    check_roles()
    uuids = set()
    for role, config in role_config.roles.iteritems():
        factory = roles.get_factory(role)
        if isinstance(config, (dict)):
            uuids.add(init_role(factory, config))
        else:
            for config_item in config:
                uuids.add(init_role(factory, config_item))

    removed_uuids = set(executing_roles.iterkeys()) - uuids
    for uuid in removed_uuids:
        executing_roles[uuid].stop()


def init_role(factory, config):
    """


    :type factory: roles.RoleFactory
    :param factory:
    :param config:
    :raise Exception:
    """
    print "Starting configuration using config: ", config
    print "Given Factory: ", factory
    if "uuid" not in config or not config["uuid"]:
        raise Exception("Invalid config. Must have a server defined UUID. Unable to continue.")
    uuid = config["uuid"]
    if uuid in executing_roles:
        print "Updating `" + uuid + "`'s config"
        executing_roles[uuid].update(config)
    else:
        print "Creating new with UUID=`" + uuid + "`"
        new_role = factory.build(config)
        executing_roles[uuid] = new_role
    return uuid





def check_roles():
    new_roles = set(role_config.roles.iterkeys())
    unconfigured_roles = new_roles - set(roles.get_factory_names())
    if unconfigured_roles:
        for role in unconfigured_roles:
            print "ERR: Not loading `%s` as it is does not have a factory." % role
            role_config.roles.pop(role) # Remove it to prevent it from saving.


def do_roles_polling():
    pass

def doRun():
    attempt_connection()
    do_roles_polling()
    reactor.run()

print dir(reactor)

doRun()
