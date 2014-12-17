:mod:`eventstreamr2.lib.amp.arguments` --- Additional argument types
======================================================

.. module:: eventstreamr2.lib.amp.arguments
    :synopsis: AMP Argument types.

The arguments defined here can be used to create new commands. To find out more see :ref:`commands-defining`.

.. note::

    This module can be included in place of :twisted:`protocols.amp`

Arguments
---------

Most :class:`Argument` subclasses accept a :code:`optional` argument to thier constructor. The arguments will error when an invalid type is provided and in the process prevent the command from being sent. If the type is unknown then use an :class:`Object` as it does not perform type checks.

.. todo::

    Figure out the difference between :class:`BoxSender` and :class:`Transport`.

.. todo::

    Figure out if the two seperate classes(:class:`BoxSender` and :class:`Transport`) are strictly required.

.. class::  BigString(optional=False)
            BigUnicode(optional=False)

    An argument that accepts an arbitary length ASCII/Unicode string.

    .. note::
        Use :class:`BigUnicode` over :class:`BigString`. This is to prevent :class:`BigString` from raising an error if the value provided is accidentaly unicode.

.. class:: Boolean(optional=False)

    An argument that accepts a :func:`bool`.

.. class:: BoxSender()

    An argument that automatically fills in the sender's information for the reciever.

    This argument is a :twisted:`protocols.amp.BoxDispatcher`; it allows access to :code:`callRemote` which can allow for a callback to send more calls to the sender.

    This is used in :mod:`manager` to update the configuration when a new station connects.

    .. note::
        :class:`BoxSender` is always optional. Any value provided is discarded prior to
        transmission.

.. class:: Float(optional=False)

    An argument that accepts a floating point number.

.. class:: Integer(optional=False)

    An argument that accepts an integer-valued number.

.. class:: Object(optional=False)

    An argument that accepts any python object.

    The implementation will use :mod:`pickle` to convert the object into a string, then send the pickled object. Then at the other end the string is unpickled and the object returned.

.. class:: Path(optional=False)

    An argument that accepts a :twisted:`python.filepath.FilePath` object.

.. class::  String(optional=False)
            Unicode(optional=False)

    An argument that accepts a ASCII/Unicode string.

    .. note::
        This argument is length limited to the limits imposed by the `AMP protocol`_ which is 65,535 bytes. Use :class:`BigString` or :class:`BigUnicode` if the length could excede this.

.. class:: Transport

    An argument that automatically fills in the sender's transport information for the reciever.

    This is used in :mod:`manager` to update the configuration when a new station connects.

    .. note::
        :class:`Transport` is always optional. Any value provided is discarded prior to
        transmission.


Command
-------

The :class:`Command` class is defined in the :twisted:`protocols.amp` module; but made avaliable here for simplicity.

.. class:: Command

    Subclass this to specify a command. See the full documentation on the :twisted:`Twisted's API documentation <protocols.amp.Command>`

    :cvar arguments:
        A list of 2-tuples of (name, Argument-subclass-instance), specifying the names and values
        of the parameters which are required for this command.

    :cvar response: A list like L{arguments}, but instead used for the return value.


.. Links ..........................................................................................

.. _AMP protocol: http://amp-protocol.net
