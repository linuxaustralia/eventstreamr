"""
Role-specific classes and methods.
"""

from twisted.application.service import MultiService

from lib.amp.mixins import InternalServiceMixin


class Role(MultiService, InternalServiceMixin, object):
    """
    A base class for roles.

    This class implements L{InternalServiceMixin} to provide access to the reactor and
    configuration objects.
    """

    def __init__(self, **kwargs):
        super(Role, self).__init__(self, **kwargs)


station_roles = []
manager_roles = []

def register_station_role(role_class):
    station_roles.append(role_class)
    return role_class

def register_manager_role(role_class):
    manager_roles.append(role_class)
    return role_class
