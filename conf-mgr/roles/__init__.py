__author__ = 'Lee Symes'


__doc__ = """

This file defines the storage for the roles.

"""

__factories__ = {}


def register_factory(name, factory):
    """Register the given factory as the given name. The factory object should be an initialised RoleFactory."""
    __factories__[name] = factory


def get_factory(name):
    """Get the factory for the name or None if no factory is registered under that name."""
    return __factories__.get(name, None)


def get_factory_names():
    """Get the names of all the factories registered."""
    return __factories__.iterkeys()


class RoleConfig(object):

    def __init__(self):
        raise Exception("Please don't initialise the RoleConfig object directly")


class RoleFactory(object):

    def __init__(self):
        pass

    def build(self, given_config):
        """
        Start a new implementation of the role using given_config to configure it.
        This method should create a new role with the given configuration. If this method is unable to make a role
        using the given configuration then it should throw an exception.

        This method should be implemented by subclasses.
        """
        return None


class SingletonRoleFactory(RoleFactory):

    def __init__(self):
        super(SingletonRoleFactory, self).__init__()
        self.instance = None

    def build(self, given_config):
        if self.instance is None or self.instance.is_stopped:
            self.instance = self.build_singleton()

        self.instance.update(given_config)

        return self.instance

    def build_singleton(self):
        """

        :rtype : SingletonRole
        """
        raise Exception("Implement build_singleton")


class Role(object):

    def update(self, config):
        pass

    def stop(self):
        pass


class SingletonRole(Role):

    def __init__(self):
        super(SingletonRole, self).__init__()
        self.is_stopped = False

    def stop(self):
        super(SingletonRole, self).stop()
        self.is_stopped = True


import pkgutil as _pkgutil
for importer, module_name, is_pkg in _pkgutil.iter_modules(__path__):
    if not is_pkg and importer is not None:
        print "Loading", module_name
        __import__("%s.%s" % (__name__, module_name))
        print "Loaded", module_name


