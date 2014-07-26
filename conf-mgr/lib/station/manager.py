__author__ = 'lee'

from twisted.application.service import MultiService
from twisted.internet.defer import DeferredList, maybeDeferred
from twisted.python import log

from lib.exceptions import InvalidConfigurationException, BlockedRoleException, MissingRoleFactoryException
from roles import get_factory, get_factory_names


class NamedMultiService(MultiService):
    """
    This MultiService only accepts children with a name defined. It also adds a utility method to support removing
    services by name without having to get the service first.
    """

    def addService(self, service):
        if service.name is None:
            raise NameError("Trying to add a service without a name. %r" % service)
        MultiService.addService(self, service)

    def removeNamedService(self, name):
        return self.removeService(self.getServiceNamed(name))

    def removeAllNamedServices(self, names, callback=None, add_name=True, *args, **kwargs):
        deferred_list = []
        for name in names:
            stop_deferred = maybeDeferred(self.removeNamedService, name)
            deferred_list.append(stop_deferred)
            if callback:
                if add_name:
                    stop_deferred.addBoth(callback, name=name, *args, **kwargs)
                stop_deferred.addBoth(callback, *args, **kwargs)
        return DeferredList(deferred_list)


class AllRolesManagerService(NamedMultiService):
    """
    """

    def __init__(self, blocked_roles=None):
        NamedMultiService.__init__(self)
        self.blocked_roles = set(blocked_roles or [])

    def configure(self, roles):
        """
        :type roles: dict[string, dict[string, object]]
        """
        self._check_all_roles_valid(roles)

        existing_roles = set(self.namedServices.iterkeys())
        updated_roles = set(roles.iterkeys())

        self.removeAllNamedServices(existing_roles - updated_roles, self.role_manager_shutdown)

        for role in updated_roles:
            if role in existing_roles:
                self.getServiceNamed(role).update_config(roles[role])
            else:
                new_manager = RoleManagerService(role)
                new_manager.update_config(roles[role])
                self.addService(new_manager)

    def role_manager_shutdown(self, result, name):
        log.msg("Completed shutdown of `%s`." % name)
        log.msg("Result of shutdown: %r" % result)
        log.msg("Current roles registered: %r" % self.namedServices.iterkeys())

    def _check_all_roles_valid(self, roles):
        """
        Ensures that all roles can be configured by this station. This includes being on the given blacklist and not
        having a factory. This method will throw a suitable subclass of `InvalidConfigurationException` if there are
        any invalid roles.

        This method also outputs descriptive information about each invalid role to the logger defined for this module.
        """
        new_roles = set(roles.iterkeys())
        factories = set(get_factory_names())
        blocked_roles = self.blocked_roles.intersection(new_roles)
        if blocked_roles:
            log.err(_why="The station was requested to run a role it is blocked from running.")
            log.err(_why="Currently blocked roles: %r" % self.blocked_roles)
            for role in blocked_roles:
                log.err(_why="`%s` is blocked from being loaded on this station" % role)
                log.err(_why="Configuration given for `%s`: %r" % (role, roles[role]))
                roles.pop(role)  # Remove it to prevent it from saving.
            raise BlockedRoleException("Invalid config file received. See logs for more information. "
                                       "Blocked Roles: %r" % blocked_roles)

        missing_roles = new_roles - factories
        if missing_roles:
            log.err(_why="Failed to locate the following factories.")
            log.err(_why="Currently defined factory names: %r" % factories)
            for role in missing_roles:
                log.err(_why="`%s` does not have a factory configured." % role)
                log.err(_why="Configuration given for `%s`: %r" % (role, roles[role]))
                roles.pop(role)  # Remove it to prevent it from saving.
            raise MissingRoleFactoryException("Invalid config file received."
                                              " Missing Roles: %r" % missing_roles)


class RoleManagerService(NamedMultiService):
    """
    A MultiService that manages a single role's services. This means that all services in this object are all providing
    an implementation of the same role.
    """

    def __init__(self, name):
        NamedMultiService.__init__(self)
        self.setName(name)

    factory = property(lambda self: get_factory(self.name), doc="Returns the factory object for the given role.")

    def update_config(self, mapped_config):
        try:
            existing_uuids = set(self.namedServices.iterkeys())
            updated_uuids = set(mapped_config.iterkeys())

            if self.factory.instances > 0 and len(updated_uuids) > self.factory.instances:
                log.err(_why="Failed to update as there are too many new uuids. %d uuids > max %d instances" %
                             (len(updated_uuids), self.factory.instances))
                log.err(_why="Recieved config: %r" % mapped_config)
                raise InvalidConfigurationException("Failed to update as there are too many new uuids. %d uuids >"
                                                    " max %d instances" % (len(updated_uuids), self.factory.instances))

            self.removeAllNamedServices(existing_uuids - updated_uuids, self.role_manager_shutdown)

            for uuid in updated_uuids:
                if uuid in existing_uuids:
                    self.getServiceNamed(uuid).update(mapped_config[uuid])
                else:
                    service = self.factory.makeService(uuid, mapped_config[uuid])
                    service.setName(uuid)
                    self.addService(service)
        except InvalidConfigurationException as e:
            raise InvalidConfigurationException("Role{%s} -> %r" % (self.name, e))

    def role_manager_shutdown(self, result, name):
        log.msg("Completed shutdown of `%s`." % name)
        log.msg("Result of shutdown: %r" % result)
        log.msg("Current uuids registered: %r" % (self.namedServices.iterkeys(), ))


def _map_uuid_to_config(config):
    """
    Returns a mapping from the uuid to the configuration(without uuid).

    :rtype: dict[string, dict[string, object]]
    """
    from copy import deepcopy
    if isinstance(config, dict):
        try:
            c = deepcopy(config)
            uuid = c.pop("uuid")
            return {uuid: c}
        except KeyError as e:
            raise InvalidConfigurationException("%r thrown whilst attempting to rearrange configuration:"
                                                " %r" % (e, config))
    else:
        d = {}
        for cfg in config:
            try:
                c = deepcopy(cfg)
                uuid = c.pop("uuid")
                d[uuid] = c
            except KeyError as e:
                raise InvalidConfigurationException("%r thrown whilst attempting to rearrange configuration:"
                                                    " %r" % (e, cfg))
        return d
