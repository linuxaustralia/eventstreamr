:mod:`eventstreamr2.lib.amp.mixins` --- Service Mixins
======================================================

.. module:: eventstreamr2.lib.amp.mixins
    :synopsis: AMP Argument types.

This module provides some basic mixins. All the mixin classes are :term:`new-style classes <new-style class>` which means that they support and rely on the correct calls to :func:`super`.

To ensure that the mixins are called(some Twisted classes are still :term:`classic class`) place them before the Twisted classes when creating a class, like the example below::

    class MyService(InternalServiceMixin, twisted.application.service.Service):
        pass


.. _lib-InternalServiceMixin:

:class:`InternalServiceMixin` --- Mixin for a better service
------------------------------------------------------------

This mixin provides the common code for storing the :code:`reactor` and the :code:`configuration manager`\(as well as any more that are required). It also has methods to create new services with these values. All new services should use this class.

.. autoclass:: InternalServiceMixin

    .. automethod:: __init__

    .. automethod:: _init_new_service


.. _lib-CommandRegistrationServiceMixin:

:class:`CommandRegistrationServiceMixin` --- Mixin for easier commands
----------------------------------------------------------------------

This mixin provides an easier method of assigning callbacks to :class:`commands <Command>`. An example of using this class is provided in the `tutorials <responding_to_command-service>`_

.. autoclass:: CommandRegistrationServiceMixin

    .. automethod:: __init__

    .. automethod:: startService

    .. automethod:: startService


.. _lib-Polling_mixins:

Polling Mixins
--------------

.. todo::
    Develop and document a new polling mixin. Preferably one that is easy to use.

.. todo::
    Write a tutorial for the polling mixins.
