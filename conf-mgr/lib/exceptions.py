__author__ = 'lee'


class InvalidConfigurationException(Exception):

    def __init__(self, message):
        super(InvalidConfigurationException, self).__init__(message)


class MissingRoleFactoryException(Exception):

    def __init__(self, message, roles=[]):
        super(MissingRoleFactoryException, self).__init__(message)
        self.roles = roles


class BlockedRoleException(Exception):

    def __init__(self, message, roles=[]):
        super(MissingRoleFactoryException, self).__init__(message)
        self.roles = roles
