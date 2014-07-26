__author__ = 'Lee Symes'
__doc__ = """
This file holds the Station configuration along with a configuration service which will update the given config when
it is requested.
"""

from copy import deepcopy

from twisted.application.service import MultiService

from lib.amp import arguments as amp_args
from lib.commands import configuration_helper, Command
from lib.exceptions import MissingRoleFactoryException, BlockedRoleException, InvalidConfigurationException
from lib.station.manager import AllRolesManagerService


class StationConfig:

    def __init__(self, roles_config=None, blocked_roles=None, station_config=None):
        """
        This class creates a root configuration for transmission or a configuration from a role configuration
         dictionary.

        If `station_config` is not specified then the configuration is taken from `roles_config` and `blocked_roles`;
            and the `ip`, `hostname` and `mac_address` are updated from the current computer's information.
        Otherwise the config is taken directly from the dictionary `station_config`. It is assumed that this dictionary
            has `ip`, `hostname`, `mac_address`, `blocked_roles` and `roles` as keys.
        """
        self._roles = {}
        self._blocked_roles = set(blocked_roles) or []
        if station_config is None:
            if roles_config is not None:
                self.roles = roles_config
            self.reset_interface_information()
        else:
            self._ip = station_config["ip"]
            self._hostname = station_config["hostname"]
            self._mac_address = station_config["mac_address"]
            self._blocked_roles = set(station_config["blocked_roles"])
            self.roles = station_config["roles"]  # Use the setter.

    @property
    def roles(self):
        """
        All the roles configured for the given station.
        :rtype : dict
        """
        return deepcopy(self._roles)
    
    @roles.setter
    def roles(self, roles):
        self._roles = deepcopy(dict(roles))

    @property
    def blocked_roles(self):
        return set(self._blocked_roles)

    ip = property(lambda self: self._ip)
    hostname = property(lambda self: self._hostname)
    mac_address = property(lambda self: self._mac_address)

    def has_role_config(self, role_name):
        return role_name in self._roles

    def get_role_config(self, role_name):
        return self._roles[role_name] if self.has_role_config(role_name) else None

    def reset_interface_information(self):
        import lib.computer_info as ci
        self._ip = ci.computer_ip()
        self._hostname = ci.computer_hostname()
        self._mac_address = ci.computer_mac_address()

    def __dict__(self):
        return {
            "ip": self.ip,
            "hostname": self.hostname,
            "mac_address": self.mac_address,
            "roles": self.roles,
            "blocked_roles": self.blocked_roles
        }

    def __str__(self):
        return "StationConfig: %s(%s;%s);" \
               " Blocked Roles: %s;" \
               " Roles: %s" % (self.hostname, self.ip, self.mac_address,
                               ", ".join(self.blocked_roles),
                               ", ".join([k for k, v in self.roles.items() if v]))

    def __repr__(self):
        return "%s(station_config=%s)" % (self.__class__, repr(self.__dict__))

# Configuration update services.

_configuration_commands = configuration_helper("Config Update Commands")


@_configuration_commands.command
class UpdateConfiguration(Command):
    arguments = [('roles', amp_args.Object())]
    response = []
    errors = {
        MissingRoleFactoryException: "MISSING_ROLE_FACTORY",
        BlockedRoleException: "ROLE_BLOCKED",
        InvalidConfigurationException: "INVALID_CONFIGURATION"}


class ConfigurationManagerService(MultiService):

    def __init__(self, role_config, update_callback=lambda: None):
        import roles
        """

        :param role_config: The configuration object loaded with all the necessary information.
        :type role_config: StationConfig
        :param update_callback:
        :type update_callback: () -> None
        :return:
        """
        MultiService.__init__(self)
        self._role_manager_service = AllRolesManagerService(role_config.blocked_roles)
        self._role_manager_service.setServiceParent(self)
        self._role_config = role_config
        self._update_callback = update_callback

    def startService(self):
        _configuration_commands.responder(UpdateConfiguration)(self.update_configuration)
        _configuration_commands.register()
        MultiService.startService(self)
        self._role_manager_service.configure(self._role_config.roles)

    def stopService(self):
        _configuration_commands.de_register()
        _configuration_commands.remove_responder(self.update_configuration)
        MultiService.stopService(self)

    def update_configuration(self, roles):
        roles = dict(roles)
        if self._role_config.roles != roles:
            self._role_manager_service.configure(roles)
            self._update_callback(roles)
        return {}





