__author__ = 'Kimberley Manning'

from lib.amp.mixins import PollingCommandServiceMixin
from roles import RoleFactory, Role, register_factory
from lib.logging import getLogger

log = getLogger(("monitoring", "general"))


class MonitoringRole(PollingCommandServiceMixin, Role):

    def __init__(self):
        log.msg("MonitoringRole")
        """
        self.config = {
            'src_ip': '10.4.4.102',
            'src_port': '1234',
            'dst_ip': '10.4.4.117',
            'dst_port': '1234'
        }
        """
        self.config = {}
        PollingCommandServiceMixin.__init__(self, 0, self.command())
        Role.__init__(self)

    def err_received(self, data):
        log.error(data)

    def command(self):
        return ['dvsink-command', 
                '-h', self.config.get('src_ip'), 
                '-p', self.config.get('src_port'),
                '--', 'dvsource-file',
                '-h', self.config.get('dst_ip'), 
                '-p', self.config.get('dst_port'),
                '-']

    def update(self, config):
        print config
        self.config = config


class MonitoringRoleFactory(RoleFactory):

    def build(self):
        return MonitoringRole()


monitoring_factory = MonitoringRoleFactory()
register_factory("monitoring", monitoring_factory)
