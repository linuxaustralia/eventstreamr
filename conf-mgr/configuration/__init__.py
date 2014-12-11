from lib.utils import Observable, AbstractPriorityDictionary



class ConfigurationManager(Observable):
    """
    This object manages sotring and accessing configurations.

    This object stores individual configurations on a 2-level hierarchy and enables the
    configurations to be ordered using an arbitary priority system.

    The 2 levels are named :code:`service_name` and :code:`source_name` to represent the service
    and the source of the configuration respectively. All configurations under a common
    :code:`service_name` are agregated using the :class:`ServiceConfigurationWrapper` which
    allows for easy access to individual configuration items.

    The priority given to :code:`set_config` is taken to mean that the larger(numerically) the
    number, the more important it is. So in the case where 2 configurations provide the same key;
    the configuration with the larger priority number will be used.

    .. note::
        For every successful modification, the observers are notified with 2 parameters:
        :code:`self` and the *service name* that is affected.

    .. warning::
        A notification of modification may not actually affect the data.

    :ivar configs: A :code:`dict` storing all the configurations.
    """


    def __init__(self):
        super(ConfigurationManager, self).__init__()
        self.configs = {}


    def __str__(self):
        import json
        return json.dumps(self.configs, indent=2)


    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, str(self))


    def get_config(self, service_name):
        """
        Gets the service's configuration wrapped in a :class:`ServiceConfigurationWrapper`.

        :param service_name: The name of the service.
        :return: A read only dictionary like object that manages retrieving the configuration in a
              transparent manner.
        """
        return ServiceConfigurationWrapper(self, service_name)

    def set_config(self, service_name, source_name, source_priority, new_config):
        """
        Assigns the given configuration to the service's configuration.

        If there is an existing (:code:`service_name`, :code:`source_name`) pair then it will be
        overwritten with the values given. The source name can be reused over multiple service
        names without any ill effects.

        :param service_name: The name of the service.
        :param source_name: The name of the source.
        :param source_priority: The priority of the source.
        :param new_config: A mapping containing the configuration.
        """
        self.configs.setdefault(service_name, {}) # Setup service name
        self.configs[service_name][source_name] = {"priority": source_priority,
                                                   "config": new_config}
        self._notify_observers(self, service_name)


    def delete_config(self, service_name, source_name=None):
        """
        Removes all configurations under :code:`service_name` and if specified :code:`source_name`.
        If :code:`source_name` is not specified all configurations a removed.

        No operation is performed if :code:`service_name` is missing, the same applies if the pair
        :code:`service_name` and :code:`source_name` are missing.

        **All** observers are notified if data is removed.

        :param service_name: The name of the service to remove.
        :param source_name: The name of source to remove.
        """
        if service_name in self.configs:
            if source_name is not None:
                if source_name in self.configs[service_name]:
                    self.configs[service_name].pop(source_name)
                else:
                    return # Prevent notification if no op performed.
            else:
                self.configs.pop(service_name)
            self._notify_observers(self, service_name)



class ServiceConfigurationWrapper(AbstractPriorityDictionary, Observable):
    """
    An immutable dictionary which allows easier access to the values stored in
    :class:`ConfigurationManager`.

    It preferable to use :meth:`get_config <ConfigurationManager.get_config>` to create an instance
    of this class.

    .. warning::
        A notification of modification may not actually affect the data.

    .. seealso::
        :class:`AbstractPriorityDictionary` for more information about the avaliable functions.

    """


    def __init__(self, config_manager, service_name):
        super(ServiceConfigurationWrapper, self).__init__()
        self.config_manager = config_manager
        self.service_name = service_name
        config_manager.add_observer(self._cfg_mgr_update)


    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.config_manager, self.service_name)


    def _cfg_mgr_update(self, mgr, service_name=None):
        """
        A callback for configuration manager.

        This notifies this object's observers if neccissary.
        """
        if service_name is None or service_name == self.service_name:
            self._notify_observers(self)

    def _ordered_configs(self):
        service_config = self.config_manager.configs.get(self.service_name, {})
        return map(lambda v: v["config"],
                   sorted(service_config.values(),
                          reverse=True, key=lambda v: v["priority"]))
