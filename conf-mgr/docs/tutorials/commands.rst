.. _tutorials-commands:

Creating and Using AMP Commands
###############################

Network communication is performed by Twisted's AMP protocol. This protocol has been modified slightly to allow commands to be enabled and disabled programatically.

To make the code in this tutorial easier; the following imports are placed at the top of the file::

    import lib.amp.arguments as amp
    from lib.commands import configuration_helper


.. _commands-defining:

Defining a Command
==================

This will show you how to define a class using the custom API's this application provides.

Defining a :meth:`configuration_helper`
---------------------------------------

Before we can define a Command, we must first define a configuration helper. This is an object which allows commands to be enabled and disabled on the fly. To create one simply::

    my_role_helper = configuration_helper("My Role")

This will create a configuration helper with the name :code:`My Role`. The name is not used anywhere except here however must be unique across the application.

Defining a Command Class
------------------------

Now that we have a command helper we can define a command. Each command is an individual class which subclasses :class:`twisted.protocols.amp.Command`. Each command should also be registered at creation with a :code:`configuration_helper`. Below is an example::

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

The lists for :code:`arguments` and :code:`response` contain a 2-tuple with the first element of the tuple being the name(see the note below) and the 2nd element is the type of the argument.

In this example, the command recieves 3 or 4 arguments:

  - :code:`full_name` --- A string of upto 65535(:code:`0xffff`) characters; any more will cause an
    error. Note that specifying :code:`amp.String` will *not* support any unicode characers.

  - :code:`author_age` --- An optional argument that is an integer. Providing a number that is not
    an integer will throw an error.

  - :code:`contact_details` --- Any python object. This allows dictionaries containing complex
    objects to be sent without the need to implement a custom transmission method.

  - :code:`large_essay` --- A string of unlimited length. Use this to avoid the length restriction
    on :code:`amp.String` and :code:`amp.Unicode`.

and responds with 1 argument:

  - :code:`mark` --- A floating point number.

To see the common arguments, see :mod:`lib.amp.arguments`

.. note::

    The names designated in command class will be used as the keywords for a call to the implementation's callback.

    **For ease of implementation**\: The names should be valid python variable names.

Responding to a command
=======================


.. _responding_to_command-service:

Responding to a command --- as a Service
========================================
