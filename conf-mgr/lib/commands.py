__author__ = 'Lee Symes'
__doc__ = """
This file contains helper functions for managing AMP commands.

"""


import twisted.protocols.amp as amp
from twisted.protocols.amp import Command

__role_locators__ = {}


class ConfiguredCommandLocator(amp.CommandLocator):

    def __init__(self):
        super(ConfiguredCommandLocator, self).__init__()

    def locateResponder(self, name):
        for locator in __role_locators__.values():
            if locator is None:
                continue
            r = locator.locate_responder(name)
            if r is not None:
                command_class, responder_func = r
                return self._wrapWithSerialization(responder_func, command_class)
        print "Failed to locate responder for ", name


class ConfiguredCommandAMP(ConfiguredCommandLocator, amp.AMP):

    def __init__(self, boxReceiver=None):
        ConfiguredCommandLocator.__init__(self)
        amp.AMP.__init__(self, boxReceiver=boxReceiver, locator=self)


class ListenableConfiguredAMP(ConfiguredCommandAMP):
    """
    This class monitors connection and disconnection

    """

    def __init__(self,
                 start=(lambda self, box_sender: None),
                 stop=(lambda self, reason: None)):
        """
        :param start: A function handle that is called when a connection starts.
        :type start: (ListenableConfiguredAMP, IBoxSender) -> None
        :param stop: A function handle that is called when a connection stops.
        :type stop: (ListenableConfiguredAMP, Failure) -> None
        """

        self._start_receiving_listener = start
        self._stop_receiving_listener = stop
        super(ListenableConfiguredAMP, self).__init__()

    def startReceivingBoxes(self, box_sender):
        r = super(ListenableConfiguredAMP, self).startReceivingBoxes(box_sender)
        self._start_receiving_listener(self, box_sender)
        return r

    def sendBox(self, box):
        print "Sending:  ", box
        super(ListenableConfiguredAMP, self).sendBox(box)

    def ampBoxReceived(self, box):
        print "Received: ", box
        super(ListenableConfiguredAMP, self).ampBoxReceived(box)

    def stopReceivingBoxes(self, reason):
        r = super(ListenableConfiguredAMP, self).stopReceivingBoxes(reason)
        self._stop_receiving_listener(self, reason)
        return r


class _ConfigurationHelper:

    def __init__(self, role_name):
        self.role_name = role_name
        self._other_cmds = set()
        self.de_register()

    ##### Configuring Command Classes #####

    def command(self, cls):
        self._configure_cmd_class(cls)
        # Don't add it to _other_cmds yet. Wait till there is a responder.
        return cls

    def _configure_cmd_class(self, cmd_class, sub_name=None):
        if sub_name is None:
            sub_name = cmd_class.__name__
        cmd_class.commandName = self.role_name + " => " + sub_name

    ##### Configuring Responder Functions #####

    def responder(self, cls, func=None):
        def decorator(fn):
            self._other_cmds.add((cls, fn))
            if __role_locators__.get(self.role_name, None):
                # Already registered so update the information.
                self.register()
        if func is None:
            return decorator
        else:
            return decorator(func)

    def remove_responder(self, cls=None, fn=None):
        if not isinstance(cls, Command):  # Support people being lazy.
            fn = cls
            cls = None

        if cls is None and fn is None:
            raise ValueError("Must specify at least one argument")
        elif cls is None:
            for clz, func in self._other_cmds:
                if func == fn:
                    cls = clz
                    break
        elif fn is None:
            for clz, func in self._other_cmds:
                if clz == cls:
                    fn = func
                    break
        # Safely remove responder by checking function & class
        try:
            self._other_cmds.remove((cls, fn))
            if __role_locators__.get(self.role_name, None):
                # Already registered so update the information.
                self.register()
            return True
        except KeyError:
            return False

    def register(self):
        locator = RoleCommandLocator(self._other_cmds)
        __role_locators__[self.role_name] = locator

    def de_register(self):
        __role_locators__.pop(self.role_name, {})


class RoleCommandLocator:

    def __init__(self, commands):
        self._commands = commands

        cmd_dict = {}
        for cmd_class, cmd_impl in commands:
            if cmd_class is None or cmd_impl is None:
                # One side is not registered so ignore it.
                continue
            cmd_dict[cmd_class.commandName] = (cmd_class, cmd_impl)

        self._cmd_dict = cmd_dict

    def locate_responder(self, name):
        if name in self._cmd_dict:
            return self._cmd_dict[name]


def configuration_helper(role_name):
    """
    Creates a configuration helper to allow for easier configuration and registration of commands.
    :param role_name:
    """
    return _ConfigurationHelper(role_name)
