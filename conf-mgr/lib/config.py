__author__ = 'Lee Symes'


"""
This file holds the data structures for the configuration of the various roles.


Notes:
 - These all implement a __dict__ method.
"""

from copy import deepcopy


class StationConfig:

    def __init__(self, roles_config=None, station_config=None):
        """
        This class creates a root configuration for transmission or a configuration from a role configuration
         dictionary.

        If this class is constructed with no arguments then the role configuration dictionary is empty.
        If this class is constructed with 1 argument then the given role configuration is stored(without copying).
        """
        if station_config is None:

            if roles_config is None:
                self.roles = {}
            else:
                self.roles = roles_config
            self.reset_interface_information()
        else:
            self.ip = station_config["ip"]
            self.hostname = station_config["hostname"]
            self.mac_address = station_config["mac_address"]
            self.roles = station_config["roles"]

    def set_roles(self, roles):
        # TODO provide a __deepcopy__ implementation for all config objects to support independent copies.
        self.roles = deepcopy(roles)

    def get_roles(self, roles):
        pass

    def has_role_config(self, role_name):
        return role_name in self.roles

    def get_role_config(self, role_name):
        return self.roles[role_name] if self.has_role_config(role_name) else None

    def reset_interface_information(self):
        import lib.computer_info as ci
        self.ip = ci.computer_ip()
        self.hostname = ci.computer_hostname()
        self.mac_address = ci.computer_mac_address()

    def __dict__(self):
        return {
            "ip": self.ip,
            "hostname": self.hostname,
            "mac_address": self.mac_address,
            "roles": self.roles
        }

    def __str__(self):
        return "StationConfig: %s(%s;%s); Roles: %s" % (self.hostname, self.ip, self.mac_address,
                                                        ", ".join([k for k, v in self.roles.items() if v]))

    def __repr__(self):
        return "%s(station_config=%s)" % (self.__class__, repr(self.__dict__))

#####################################################ROLE CONFIG########################################################
#
# Role configuration classes.
#
########################################################################################################################
