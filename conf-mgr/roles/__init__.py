__author__ = 'Lee Symes'

import twisted.protocols.amp as amp

__doc__ = """

This file defines the storage for the roles.

"""


__role_locators__ = {}


class ConfiguredCommandLocator(amp.CommandLocator):

    def __init__(self):
        print "Inside", repr(__role_locators__)
        pass

    def locateResponder(self, name):
        for locator in __role_locators__.values() :
            if locator is None:
                continue
            r = locator.locate_responder(name)
            if r is not None:
                commandClass, responderFunc = r
                return self._wrapWithSerialization(responderFunc, commandClass)
        print "Failed to locate responder for ", name


class ConfiguredCommandAMP(amp.AMP, ConfiguredCommandLocator):
    
    def __init__(self, boxReceiver=None):
        amp.AMP.__init__(self, boxReceiver=boxReceiver, locator=self)
        self.transport

    def locateResponder(self, name):
        return ConfiguredCommandLocator.locateResponder(self, name)


class _ConfigurationHelper:

    def __init__(self, role_name):
        self.role_name = role_name
        self._start_cmd = [None, None]
        self._update_cmd = [None, None] # Not used
        self._stop_cmd = [None, None]
        self._other_cmds = []
        self.de_register()

    ##### Configuring Command Classes #####

    def _start_command(self, cls):
        self._configure_cmd_class(cls, "start")
        self._start_cmd[0] = cls
        return cls

    def _stop_command(self, cls):
        self._configure_cmd_class(cls, "stop")
        self._stop_cmd[0] = cls
        return cls

    def _command(self, cls):
        self._configure_cmd_class(cls)
        # Don't add it to _other_cmds yet. Wait till there is a responder.
        return cls

    ##### Configuring Responder Functions #####

    def _start_responder(self, fn):
        self._start_cmd[1] = fn

    def _stop_responder(self, fn):
        self._stop_cmd[0] = fn

    def _responder(self, cls):
        print "Responder decorator for",self.role_name, " -- ", cls
        def decorator(fn):
            print "Decorating for",self.role_name, " -- ", cls, " -- ",fn
            self._other_cmds.append((cls, fn))
        return decorator



    def _configure_cmd_class(self, cmd_class, sub_name=None):
        if sub_name is None:
            sub_name = cmd_class.__name__
        cmd_class.commandName = self.role_name + "__" + sub_name


    def register(self):


        locator = RoleCommandLocator(self._start_cmd, self._update_cmd, self._stop_cmd, self._other_cmds[:])
        __role_locators__[self.role_name] = locator

        # Now prevent further modification which could produce unexpected results(mainly commands not being fired).
        def configured(*args, **kwargs):
            raise Exception("The configuration class for %s role is already configured." % (self.role_name, ) +
                            " Please move this call or the configure call.")

        # TODO: Decorate these functions so that the following happens:
        #  self.de_register()
        #  original_fn_call(*args, **kwargs)
        #  self.register()
        # This way they are always callable; and it's still cheap to do when this is not registered.
        # Keep de_register the same so that when a function is called it doesn't accidentally register it.
        self.start_command = self.stop_command = self.command = configured
        self.start_responder = self.stop_responder = self.responder = configured

    def de_register(self):
        # Remove the key. Discard the locator because chances are it will be changed.
        __role_locators__.pop(self.role_name, {})

        # De-registered so you are more than welcome to register new commands.
        self.start_responder = self._start_responder
        self.stop_responder = self._stop_responder
        self.responder = self._responder

        self.start_command = self._start_command
        self.stop_command = self._stop_command
        self.command = self._command


class RoleCommandLocator:

    def __init__(self, start_cmd, update_cmd, stop_cmd, other_cmds):
        self._start_cmd = start_cmd
        self._update_cmd = update_cmd
        self._stop_cmd = stop_cmd
        self._other_cmds = other_cmds

        cmd_dict = {}
        for cmd_class, cmd_impl in [self._start_cmd, self._update_cmd, self._stop_cmd] + self._other_cmds:
            print "Examining: (%s, %s)" % (cmd_class, cmd_impl)
            if cmd_class is None or cmd_impl is None:
                continue
            print "Registering %s(Class:%s) to call %s" % (cmd_class.commandName, cmd_class.__name__, str(cmd_impl))
            cmd_dict[cmd_class.commandName] = (cmd_class, cmd_impl)

        self._cmd_dict = cmd_dict

    def locate_responder(self, name):
        print "Checking ", name, " in ", repr(self._cmd_dict)
        if name in self._cmd_dict:
            return self._cmd_dict[name]



def configuration_helper(role_name):
    return _ConfigurationHelper(role_name)


import pkgutil as _pkgutil
for importer, module_name, is_pkg in _pkgutil.iter_modules(__path__):
    if not is_pkg and importer is not None:
        print "Loading", module_name
        __import__("%s.%s" % (__name__, module_name))
        print "Loaded", module_name


