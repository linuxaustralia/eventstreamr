.. _tutorials-commands:

AMP Command Primer
##################

Network communication is performed by Twisted's AMP protocol. This protocol has been modified
slightly to allow commands to be enabled and disabled programatically.

To make the code in this tutorial easier; the following imports are placed at the top of the file::

    import eventstreamr2.lib.amp.arguments as amp
    from eventstreamr2.lib.commands import configuration_helper


.. _commands-defining:

Defining a Command
==================

This will show you how to define a class using the custom API's this application provides.

Defining a :meth:`configuration_helper`
---------------------------------------

Before we can define a Command, we must first define a configuration helper. This is an object
which allows commands to be enabled and disabled on the fly. To create one simply::

    my_role_helper = configuration_helper("My Role")

This will create a configuration helper with the name :code:`My Role`. The name is not used
anywhere except here however must be unique across the application.

Defining a Command Class
------------------------

Now that we have a command helper we can define a command. Each command is an individual class
which subclasses :class:`twisted.protocols.amp.Command`. Each command should also be registered
at creation with a :code:`configuration_helper`. Below is an example::

    @my_role_helper.command
    class MyRolesCustomCommand(amp.Command):
        arguments = [
                        ('full_name', amp.Unicode()),
                        ('author_age', amp.Integer(optional=True)),
                        ('contact_details', amp.Object()),
                        ('large_essay', amp.BigUnicode())
                    ]
        response = [
                        ('mark', amp.Float())
                   ]

The lists for :code:`arguments` and :code:`response` contain a 2-tuple with the first element of
the tuple being the name(see the note below) and the 2nd element is the type of the argument.

In this example, the command recieves 3 or 4 arguments:

  - :code:`full_name` --- A string of upto 65535(:code:`0xffff`) characters; any more will cause an
    error. Note that specifying :code:`amp.String` will *not* support any unicode characers.

  - :code:`author_age` --- An optional argument that is an integer. Providing a number that is not
    an integer will cause an error.

  - :code:`contact_details` --- Any python object. This allows dictionaries containing complex
    objects to be sent without the need to implement a custom transmission method.

  - :code:`large_essay` --- A string of unlimited length. Use this to avoid the length restrictions
    on :code:`amp.String` and :code:`amp.Unicode`.

and responds with 1 argument:

  - :code:`mark` --- A floating point number.

To see the common arguments, see :mod:`lib.amp.arguments`

.. note::

    The names designated in command class will be used as the keywords for a call to the implementation's callback.

    **For ease of implementation**\: The names should be valid python variable names.

.. _making_a_call_to_a_command:

Calling a command
=================

Call :code:`callRemote` on a :code:`BoxSender`::

    args = {"full_name": "Joe Blogs",
            "author_age": 19,
            "contact_details": {
                    "complex": "objects",
                    "with":
            },
            "large_essay": ("I wrote this eassay in a matter of minutes. " * 1000)
        }
    # Call using kwargs.
    box_sender.callRemote(MyRolesCustomCommand, **args)


.. _responding_to_command-non-service:

Responding to a command
=======================

To register a responder to a command simply call :func:`responder <ConfigurationHelper.responder>`
on the :code:`my_role_helper`::

    def my_command_responder(full_name, author_age, contact_details, large_essay):
        from random import random
        # I'm a great marker
        return {"mark": random()}

    my_role_helper.responder(MyRolesCustomCommand, my_command_responder)

Then when the responder is no longer needed; it can be removed::

    my_role_helper.remove_responder(MyRolesCustomCommand, my_command_responder)

.. note::

    This should not be used if it is related to a service(
    `see below <_responding_to_command-service>`_)


.. _responding_to_command-service:

Responding to a command --- as a Service
========================================

Firstly setup your Service::

    from eventstreamr2.lib.amp.mixins import CommandRegistrationServiceMixin
    from eventstreamr2.lib.amp.mixins import InternalServiceMixin
    from twisted.application.service import Service

    class MyCommandService(CommandRegistrationServiceMixin,
                            InternalServiceMixin,
                            Service):

        def __init__(self, **kwargs):
            # Define the responders here:
            kwargs["command_responder_pairs"] = [
                (MyRolesCustomCommand, self.my_command_responder)
            ]
            super(MyCommandService, self).__init__(**kwargs)

        def my_command_responder(full_name, author_age, contact_details, large_essay):
            from random import random
            # I'm a great marker
            return {"mark": random()}

Once this service is started the responder(s) are registered; then when the service is stopped
the responder(s) are removed.
