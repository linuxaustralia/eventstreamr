# __author__ = 'Kimberley Manning'
#
# from lib.amp.mixins import PollingCommandServiceMixin
# from roles import RoleFactory, Role, register_factory
# from lib.logging import getLogger
#
# class MonitoringRole(PollingCommandServiceMixin, Role):
#
#     def __init__(self, uuid):
#         self.log = getLogger(("monitoring", uuid))
#         self.config = {}
#         PollingCommandServiceMixin.__init__(self, 0)
#         Role.__init__(self)
#
#     def err_received(self, data):
#         self.log.cmd_output_stderr(data)
#
#     def out_received(self, data):
#         self.log.cmd_output_stdout(data)
#
#     def startService(self):
#         PollingCommandServiceMixin.startService(self)
#         Role.startService(self)
#
#     def command(self):
#         if "src_ip" not in self.config:
#             raise Exception("Too Early")
#         return ['dvsink-command',
#                 '-h', self.config.get('src_ip'),
#                 '-p', self.config.get('src_port'),
#                 '--',
#                 'dvsource-file',
#                 '-h', self.config.get('dst_ip'),
#                 '-p', self.config.get('dst_port'),
#                 '-']
#
#     def update(self, config):
#         self.config = config
#
#
# class MonitoringRoleFactory(RoleFactory):
#
#     def build(self, uuid):
#         return MonitoringRole(uuid)
#
#
# monitoring_factory = MonitoringRoleFactory()
# register_factory("monitoring", monitoring_factory)
