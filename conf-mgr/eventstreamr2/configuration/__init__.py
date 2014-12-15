from eventstreamr2.utils.events import Observable
from eventstreamr2.utils.collections import AbstractPriorityDictionary



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
        For every successful modification, the observers are notified with 0 or 1 parameters:

         - *Service Name* if there is only a single service affected.

    .. warning::
        A notification of modification may not actually affect the data.

    .. todo::
        Change the keying order for internal storage to :code:`source` -> :code:`service`. And
        change the priority to be located under the :code:`source` key(not :code:`service`).


    :ivar configs: A :code:`dict` storing all the configurations.
    """

    _priority_key = object()

    def __init__(self):
        super(ConfigurationManager, self).__init__()
        self._configs = {}


    def __str__(self):
        import json
        return json.dumps(self._configs, indent=2)


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

    def set_source_priority(self, source_name, new_source_priority):
        self._configs.setdefault(source_name, {}) # Setup source name dictionary
        self._configs[source_name][self._priority_key] = new_source_priority

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
        self._configs.setdefault(source_name, {}) # Setup source name dictionary
        self._configs[source_name][self._priority_key] = source_priority
        self._configs[source_name][service_name] = new_config
        self._notify_observers(service_name)


    def delete_source(self, source_name):
        if source_name in self._configs:
            self._configs.pop(source_name)
            self._notify_observers()


    def delete_service_config(self, service_name, source_name=None):
        """
        Removes all configurations under :code:`service_name` and if specified :code:`source_name`.
        If :code:`source_name` is not specified all configurations a removed.

        No operation is performed if :code:`service_name` is missing, the same applies if the pair
        :code:`service_name` and :code:`source_name` are missing.

        .. note::
            This will only fire listeners when it modifies the underlying data. It may not
            actually change the *end-user* data.

        :param service_name: The name of the service to remove.
        :param source_name: The name of source to remove.
        """
        if source_name is not None:
            if source_name in self._configs:
                self._configs[source_name].pop(service_name)
                self._notify_observers(service_name)
        else:
            modified = False
            for source_cfg in self._configs.values():
                if service_name in source_cfg:
                    source_cfg.pop(service_name)
                    modified = True
            if modified:
                self._notify_observers(service_name)



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
        config_manager.add_weak_observer(self._cfg_mgr_update)


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
        name = self.service_name
        src_cfgs = sorted(self.config_manager._configs.values(),
                        reverse=True,
                        key=lambda v: v[ConfigurationManager._priority_key])

        for src_cfg in src_cfgs:
            if self.service_name in src_cfg:
                yield src_cfg[self.service_name]
