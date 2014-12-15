"""
This module provides some basic mixin classes to be used when implementing Twisted services.
"""


class InternalServiceMixin(object):
    """
    A base class that provides easier implementation of sub-services. It automatically initilises
    the configuration manager and reactor passed in.

    To use simple extend this class and define your init method as shown::

        def __init__(self, ..., **kwargs):
            super(..., self).__init__(self, **kwargs)
            ...

    :ivar _config_mgr: A configuration manager instance which contains all the configurations.
    :type _config_mgr: :class:`ConfigurationManager <configuration.ConfigurationManager>`
    :ivar _reactor: A twisted reactor instance to be used for this service. Use this over importing
                    :code:`twisted.internet.reactor` as it allows for easier testing.
    """


    def __init__(self, *args, **kwargs):
        """
        This method initilises the service with the configuration manager and reactor passed in as
        keyword args.

        :param _config_mgr: The configuration manager for this service(KW args only)
        :param _reactor: The reactor for this service(KW args only)
        """
        self._config_mgr = kwargs["_config_mgr"]
        self._reactor = kwargs["_reactor"]
        super(ConfMgrService, self).__init__(self, *args, **kwargs)


    def _init_new_service(self, service_class, *args, **kwargs):
        """
        Create a new service using this service's configuration manager and reactor. Additional
        parameters after the :code:`service_class` will be passed through to the class's
        constructor.

        :param service_class: The service class to create.
        :param \*args: The positional arguments to send to the service class's constructor.
        :param \*\*kwargs: The keyword arguments to send to the service class's constructor. Note
                         that :code:`_config_mgr` and :code:`_reactor` are always overwritten.
        """
        kwargs["_config_mgr"] = _config_mgr
        kwargs["_reactor"] = _reactor
        return service_class(*args, **kwargs)



class CommandRegistrationServiceMixin(object):
    """
    This mixin allows services to dictate the responders for a set of commands; then have them
    automatically registered and de-registered when the service is started and stoped.

    .. todo::
        Add methods to change the command bindings on the fly.

    .. todo::
        Consider changing this to use a class variable for the :code:`responder_pairs` and then
        binding them to :code:`self` when the service is started.
    """


    def __init__(self, helper, command_responder_pairs, *args, **kwargs):
        """
        Simply provide the configuration helper and then a list

        :param helper: The configuration helper the commands provided are attached to.
        :type helper: eventstreamr2.lib.commands.ConfigurationHelper
        :param command_responder_pairs: A list of 2-tuples mapping a command to a function.
        :type command_responder_pairs: list(tuple(Command, function))
        """
        self._helper = helper
        self._command_pairs = command_responder_pairs
        super(CommandRegistrationServiceMixin, self).__init__(*args, **kwargs)


    def startService(self):
        """
        Registers the command-responder pairs given in the constructor with the configuration
        helper also given in the constructor.
        """
        for command, responder in self._command_pairs:
            self._helper.responder(command, responder)
        self._helper.register()

        super(CommandRegistrationServiceMixin, self).startService()


    def stopService(self):
        """
        Registers the command-responder pairs given in the constructor with the configuration
        helper also given in the constructor.
        """
        for command, responder in self._command_pairs:
            self._helper.remove_responder(command, responder)

        super(CommandRegistrationServiceMixin, self).stopService()
