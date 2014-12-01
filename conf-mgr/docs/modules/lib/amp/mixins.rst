:mod:`lib.amp.mixins` --- Service Mixins
========================================

.. module:: lib.amp.mixins
    :synopsis: AMP Argument types.

This module provides some basic mixins. All the mixin classes are :term:`new-style classes <new-style class>` which means that they support and rely on the correct calls to :func:`super`.

To ensure that the mixins are called(some Twisted classes are still :term:`classic class`) place them before the Twisted classes when creating a class, like the example below::

    class MyService(InternalServiceMixin, twisted.application.service.Service):
        pass

:class:`InternalServiceMixin` --- Mixin for a better service
------------------------------------------------------------

This mixin provides the common code for storing the :code:`reactor` and the :code:`configuration manager`\(as well as any more that are required). It also has methods to create new services with these values. All new services should use this class.

.. autoclass:: InternalServiceMixin

    .. automethod:: _init_new_service

    .. automethod:: __init__
