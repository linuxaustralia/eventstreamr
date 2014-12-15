__author__ = 'Lee Symes'


from twisted.protocols import amp

from eventstreamr2.lib.amp import arguments as amp_args
from eventstreamr2.lib.commands import configuration_helper


# TODO rename this stuff.

manager_commands = configuration_helper("manager")
station_commands = configuration_helper("station")

@manager_commands.command
class RegisterStationCommand(amp.Command):
    arguments = [('config', amp_args.Object()),
                 ('transport', amp_args.Transport()),
                 ('box_sender', amp_args.BoxSender())]
    response = []
