__author__ = 'Lee Symes'


from twisted.protocols import amp

from lib.amp import arguments as amp_args
from lib.commands import configuration_helper


manager_commands = configuration_helper("manager")
station_commands = configuration_helper("station")

@manager_commands.command
class RegisterStationCommand(amp.Command):
    arguments = [('config', amp_args.Object()),
                 ('transport', amp_args.Transport())]
    response = []




