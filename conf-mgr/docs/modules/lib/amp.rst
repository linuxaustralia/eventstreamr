:mod:`lib.amp` --- An extension of Twisted's AMP Implementaion
==============================================================

.. module:: lib.amp


This package provides extensions for Twisted's AMP API. These include more flexible arguments and
an API to dynamically enable and disable commands.

:mod:`lib.amp.arguments` --- Additional argument types
------------------------------------------------------

.. module:: lib.amp.arguments
    :synopsis: AMP Argument types.

The arguments defined here can be used to create new commands. To find out more see :ref:`commands-defining`.

.. note::

    This module can be included in place of :mod:`twisted.protocols.amp`

Arguments
~~~~~~~~~

Most :class:`Argument` subclasses accept a :code:`optional` argument to thier constructor. The arguments will error when an invalid type is provided and in the process prevent the command from being sent. If the type is unknown then use an :class:`Object` as it does not perform type checks.

.. class:: BigString(optional=False)

    An argument that accepts an arbitary length ASCII string.

    .. note::
        It is better to use :class:`BigUnicode` as unicode support is built-in.

.. class:: BigUnicode(optional=False)

    An argument that accepts an arbitary length unicode string.

.. class:: Boolean(optional=False)

    An argument that accepts a :func:`bool`.

.. class:: BoxSender()

    An argument that automatically fills in the sender's information for the reciever.

    This argument is a :class:`twisted.protocols.amp.BoxDispatcher`; it allows access to :code:`callRemote` which can allow for a callback to send more calls to the sender.

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

    An argument that accepts a :class:`twisted.python.filepath.FilePath` object.

.. class:: String(optional=False)


.. class:: Transport

    An argument that

    .. note::
        :class:`Transport` is always optional. Any value provided is discarded prior to
        transmission.

.. class:: Unicode(optional=False)



.. class:: Command
