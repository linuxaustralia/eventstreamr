
(I) --- Creating and configuring services
=========================================

.. note::

    **This has been implemented**. This plan is no longer needed as it has been implemented in :class:`lib.amp.mixins.InternalServiceMixin`

All internal services will be constructed using a reactor argument. This allows for easier testing
and also follows the coding convention set down by Twisted.

Each service will also recieve a configuration manager instance. And as the list of these increases
I have decided to provide a mixin with allows all this to be configured without the need to
replicate the same code repeatedly. ::

    SomeInternalService(..., _reactor=reactor, _config_mgr=configuration_manager)

Each service can override the following mixin to allow all of this to be configured::

    class InternalServiceMixin(object):
      def __init__(self, *args, **kwargs):
        self._reactor = kwargs["_reactor"]
        self._config_mgr = kwargs["_config_mgr"]

Then all that classes need to do to implement it is take their args, add a `**kwargs` to their
parameter list and simply pass it up the chain using super. It will eventually reach this mixin
class and setup the reactor and config manager.

This class should also have other methods that make it easier to create new services using the
configuration from the current one. As both the reactor and the config manager are not
service-dependant a function such as the one below would allow for the easier creating of a new
internal service. ::

    class InternalServiceMixin(object):

      # ...

      def _init_new_service(self, service_class, *args, **kwargs):
        kwargs["_config_mgr"] = _config_mgr
        kwargs["_reactor"] = _reactor
        return service_class(*args, **kwargs)
