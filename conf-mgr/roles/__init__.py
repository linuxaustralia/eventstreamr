__author__ = 'Lee Symes'
__doc__ = """

This file defines the storage for the roles.

"""

import pkgutil as _pkgutil

from twisted.application.service import MultiService

from lib.logging import getLogger
from lib.amp.mixins import PollingCommandServiceMixin

__factories = {}
__loaded_roles = []

log = getLogger(["roles-init"])


def register_factory(name, factory):
    """Register the given factory as the given name. The factory object should be an initialised RoleFactory."""
    log.msg("Registering %s with the given factory: %r" % (name, factory))
    __factories[name] = factory


def get_factory(name):
    """
    Get the factory for the name or None if no factory is registered under that name.

    :rtype: RoleFactory
    """
    __check_load()
    return __factories.get(name, None)


def get_factory_names():
    """Get the names of all the factories registered."""
    __check_load()
    return __factories.iterkeys()


class RoleFactory(object):
    """

    :type instances: int
    :cvar instances: The maximum number of instances that are allowed to be running at any given time. This should
                      not be managed through this factory as it is managed higher in the chain. Set to 0 or less for
                      any number of instances running at a given time.
    """

    instances = 0

    def __init__(self):
        pass

    def makeService(self, uuid, given_config):
        """
        Start a new implementation of the role using given_config to configure it.
        This method should create a new role with the given configuration. If this method is unable to make a role
        using the given configuration then it should throw an exception.

        This method's default operation is to create an instance using `build` and then configure it using
        `Role.update`.
        """
        instance = self.build(uuid)
        instance.update(given_config)

        return instance

    def build(self, uuid):
        """
        Implement this method to return a new role. The role will be configured using `Role.update`. If more advanced
        configuration is needed, then implement `makeService`

        :rtype: Role
        """
        return None


class Role(MultiService, object):
    """
    This class is safe to be implemented with MultiService as it provides no implementations of Service methods.
    """

    def __init__(self):
        MultiService.__init__(self)

    def startService(self):
        print "Starting Role %s" % self.name
        self.start()
        MultiService.startService(self)

    def stopService(self):
        print "Starting Role"
        self.stop()
        MultiService.stopService(self)

    def start(self):
        pass

    def update(self, config):
        pass

    def stop(self):
        pass


class WatchdogRole(Role, PollingCommandServiceMixin):

    def __init__(self, poll_length=0, command=None):
        Role.__init__(self)
        PollingCommandServiceMixin.__init__(self, poll_length, command)

    def startService(self):
        PollingCommandServiceMixin.startService(self)
        Role.startService(self)

    def stopService(self):
        PollingCommandServiceMixin.stopService(self)
        Role.stopService(self)

    def out_received(self, data):
        try:
            self.log.cmd_output_stdout(data)
        except NameError:
            pass

    def err_received(self, data):
        try:
            self.log.cmd_output_stderr(data)
        except NameError:
            pass

# TODO make this a function that doesn't get called when testing ect.


def __check_load():
    if __loaded_roles:
        return
    __loaded_roles.append("Hello") # Prevent recursive call.
    loaded = []
    for importer, module_name, is_pkg in _pkgutil.iter_modules(__path__):
        if not is_pkg and importer is not None:
            log.msg("Loading `%s` module ..." % module_name)
            __import__("%s.%s" % (__name__, module_name))
            log.msg("Loaded `%s` module." % module_name)
            loaded.append(module_name)

    log.msg("Loaded the following modules: %r" % loaded)
    del loaded
