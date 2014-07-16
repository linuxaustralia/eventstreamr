__author__ = 'Lee Symes'


__doc__ = """

This file defines the storage for the roles.

"""


class RoleConfig(object):

    def __init__(self):
        raise Exception("Please don't initialise the RoleConfig object directly")


class RoleFactory(object):

    def __init__(self):
        pass

    def build(self, given_config):
        """
        Start a new implementation of the role using given_config to configure it.
        This method should return a dictionary laid out as follows:
        {
         "object": The actual implementation.
         "config":
        }
        Where the config pair is optional and should be used if the `given_config` needs to be updated.
        If `given_config` is updated then the uuid MUST NOT change.

        This method should be implemented by subclasses.
        """
        return {"object": None, "config": given_config}


class SingletonRoleFactory(RoleFactory):

    def __init__(self):
        super(SingletonRoleFactory, self).__init__()
        self.instance = None

    def build(self, given_config):
        if self.instance is None or self.instance.is_stopped:
            self.instance = self.build_singleton()

        updated_config = self.instance.update(given_config)

        if updated_config is not None:
            return {"object": self.instance, "config": updated_config}
        else:
            return {"object": self.instance}

    def build_singleton(self):
        """

        :rtype : SingletonRole
        """
        raise Exception("Implement build_singleton")


class Role(object):

    def update(self, config):
        return None

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


