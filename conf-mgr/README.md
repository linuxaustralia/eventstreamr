Conference Manager
==================

This project aims to reimplement the EventStreamr in Python.

This project currently has the following dependencies:

 - Commands: `ifdata` and `hostname`
 - Python 2.7.8
 - PIP packages:
   - `Twisted` (currently version 14.0.0)

This may also require PIP packages `pyOpenSSL` and `service_identity` if SSL is required. Otherwise it produces the following warning:
`/Library/Python/2.7/site-packages/twisted/internet/_sslverify.py:184: UserWarning: You do not have the service_identity module installed. Please install it from <https://pypi.python.org/pypi/service_identity>. Without the service_identity module and a recent enough pyOpenSSL tosupport it, Twisted can perform only rudimentary TLS client hostnameverification.  Many valid certificate/hostname mappings may be rejected.`

Running the files
-----------------

To run the manager, simply execute `python -m manager`

To run the station, simply execute `twistd --nodaemon --python station.py` or for daemon mode: `twistd --python station.py`.
For more information on daemon mode and `twistd`, see the [Twisted Documentation](http://twistedmatrix.com/documents/current/core/howto/basics.html)

Manager/Station Communication
-----------------------------

The following assumes that the manager is currently running and that the station is able to communicate with the manager.

 1. The station connects to the manager.
 2. The station sends it's current configuration which includes IP(though not required), hostname, MAC address and currently configured roles(Using `lib.general_commands.RegisterStationCommand`). This request isn't responded to in any order.
 3. The manager sends a(separate) request to the station with the up to date role config(may be the same as sent in step 2)(Using `lib.config.UpdateConfiguration`).
 4. The station responds to the request in step 3 to indicate if the configuration was successful. This is indicated by no exception being thrown. If the configuration is invalid then one of `InvalidConfigurationException`, `MissingRoleFactoryException` or `BlockedRoleException`(all from `lib.exceptions`) is thrown with a descriptive error message. This message is enough to determine the problem without having to access the station's logs.

Using this mechanism of the manager notifying the station of updates will reduce polling for updates and disconnects the 'Hello' request from updating the role's configurations.

Implementing A New Role
-----------------------

 1. Create a python file in `roles`. This file will be auto-loaded when `roles` is imported.
 2. Add the following import to the top of the file. This are required to create a basic role.
  `from roles import RoleFactory, Role, register_factory`
 3. Implement `Role` implementing `__init__`, `startService`, `update` and `stopService` as necessary. Keep the super calls(or remove any unused methods)

        class <<Role Class Name>>(Role):

            def __init__(self, ...):
                super(<<Role Class Name>>, self).__init__()

            def startService(self):
                super(<<Role Class Name>>, self).startService()

            def update(self, config):
                pass #  Doesn't need super as Role doesn't do anything in `update`

            def stopService(self):
                super(<<Role Class Name>>, self).stopService()

    Note that the service will not be running when `__init__` is called so defer as much setup to `startService`.

 4. Implement `RoleFactory` as below, replacing the instances count with the maximum number of instances allowed(or 0 if infinite):

        class <<Role Factory Class Name>>(RoleFactory):

            instances = ?

            def __init__(self, ...):
                super(<<Role Factory Class Name>>, self).__init__()

            def build(self):
                return <<Role Class Name>>(...)

  5. This provides the basic skeleton for the `Role` and `RoleFactory`. Now call `register_factory("<<Role Name>>", <<Role Factory Class Name>>(...))` where `<<Role Name>>` is the name used in the configuration. If this name does not match exactly(including case) then the role will fail to load.

Implementing Custom Commands for the Role
-----------------------------------------

This assumes that you already have a `Role`. It is also best if this role is a singleton(I.E. `instances = 1` in the `RoleFactory` implementation).

 1. Add the following imports:

        from lib.amp import arguments as amp
        from lib.commands import configuration_helper

 2. Create a command helper(replace `_role_commands` with something more descriptive).

        _role_commands = configuration_helper("Some descriptive name(with any characters)")

    This provides helper methods for configuring `Command`s with non-clashing names and linking them with callbacks dynamically.

 3. Now create a command. For a more descriptive tutorial see the [documentation](http://twistedmatrix.com/documents/current/core/howto/amp.html#commands). All required classes are included in `lib.amp.arguments` which is imported as `amp`. Below is an example command that receives a string and an object and returns a integer:

        @_encode_job_station.command
        class <<Command Name>>(amp.Command):
            arguments = [('var_name1', amp.Unicode()),
                         ('var_name2', amp.Object()]
            response = [('processes_running', amp.Integer())]

    This creates a command(`<<Command Name>>`) and configures it's name. The command sends a unicode string as `var_name1` and a generic object(encoded using pickle) as `var_name2`; it receives an integer as `processes_running`. The naming will become clear when the callback is implemented.

 4. Now create a method whose arguments(in any order) are those named in `arguments`. If placing it in any class(as below) then add the `self` as that is filled by Python:

        class <<Role Class Name>>(Role):
            ...
            def callback_or_any_name_you_want(self, var_name1, var_name2):
                ...  # Do something useful(or not - it's up to you)
                return {'processes_running': 10}

    This is now a callback that is ready to be added and configured. Note that the return is a dictionary. If the `response` list was empty then an empty dictionary must be returned.

 5. Now to register the callback and the command. This is best done in the `startService` in the `Role` implementation:

        class <<Role Class Name>>(Role):
            ...
            def startService(self):
                _role_commands.responder(<<Command Name>>)(self.callback_or_any_name_you_want)
                super(<<Role Class Name>>, self).startService()

    This simply registers the link between the Command and the callback.
 6. Now to actually allow the command to be called:

        class <<Role Class Name>>(Role):
            ...
            def startService(self):
                _role_commands.responder(<<Command Name>>)(self.callback_or_any_name_you_want)
                _role_commands.register()
                super(<<Role Class Name>>, self).startService()

    This will now allow the callback to be fired when the command is called.

 7. Now to de-register & remove the command when the service stops:

        class <<Role Class Name>>(Role):
            ...
            def stopService(self):
                _role_commands.de_register()
                _role_commands.remove_responder(<<Command Name>>, self.callback_or_any_name_you_want)
                super(<<Role Class Name>>, self).stopService()

    This not only prevents the command from being called, it removes any trace of the command/callback pair so that it cannot be accidentally re-registered.


