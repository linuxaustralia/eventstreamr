from collections import OrderedDict
from lib.logging import getLogger
from twisted.application.service import MultiService
from lib.utils import Observable

_log = getLogger(("lib", "configuratuion", "__init__"))


class ConfigurationManager(MultiService, Observable):
    """
    This object manages sotring and accessing configurations.

    This object stores individual configurations on a 2-level hierarchy and enables the configurations to be ordered using an arbitary priority system.

    The 2 levels are named C{service_name} and C{source_name} to represent the service and the source of the configuration respectively. All configurations under a common `service_name` are agregated using the L{ServiceConfigurationWrapper} which allows for easy access to individual configuration items.

    The priority given to C{set_config} is taken to mean that the larger(numerically) the number, the more important it is. So in the case where 2 configurations provide the same key; the configuration with the larger priority number will be used.

    All observers will be called with 2 parameters; this object and the service name that was updated. Note that it is possible that when an event is fired, the end-user data has not changed. For example removing a non-existant source will fire an event without the configuration being changed.

    @ivar configs: A C{dict} storing all the configurations.
    """

    def __init__(self):
        super(ConfigurationManager, self).__init__()
        self.configs = {}

    def __str__(self):
        import json
        return json.dumps(self.configs, indent=2)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, str(self))

    def set_config(self, service_name, source_name, source_priority, new_config):
        """
        Assigns the given configuration to the service's configuration.

        If there is an existing (C{service_name}, C{source_name}) pair then it will be overwritten with the values given. The source name can be reused over multiple service names without any ill effects.

        @param service_name: The name of the service.
        @param source_name: The name of the source.
        @param source_priority: The priority of the source.
        @param new_config: A mapping containing the configuration.
        """
        self.configs.setdefault(service_name, {}) # Setup service name
        self.configs[service_name][source_name] = {"priority": source_priority,
                                                   "config": new_config}
        self._notify_observers(self, service_name)

    def get_config(self, service_name):
        """
        Assigns the given configuration to the service's configuration.

        If there is an existing (C{service_name}, C{source_name}) pair then it will be overwritten with the values given. The source name can be reused over multiple service names without any ill effects.

        @param service_name: The name of the service.
        @return: A read only dictionary like object that manages retrieving the configuration in a transparent manner.
        @rtype: L{ServiceConfigurationWrapper}
        """
        return ServiceConfigurationWrapper(self, service_name)

    def delete_config(self, service_name, source_name=None):
        if service_name in self.configs:
            if source_name is not None:
                self.configs[service_name].pop(source_name, None)
            else:
                self.configs.pop(service_name)
            self._notify_observers(self, service_name)


class ServiceConfigurationWrapper(AbstractPriorityDictionary, Observable):

    def __init__(self, config_manager, service_name):
        super(ServiceConfigurationWrapper, self).__init__()
        self.config_manager = config_manager
        self.service_name = service_name
        config_manager.add_observer(self._cfg_mgr_update)

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.config_manager, self.service_name)

    def _cfg_mgr_update(self, mgr, service_name=None):
        if service_name is None or service_name == self.service_name:
            self._notify_observers(self)

    def service_config(self):
        return self.config_manager.configs.get(self.service_name, {})

    def ordered_configs(self):
        return map(lambda v: v["config"],
                   sorted(self.service_config().values(),
                          reverse=True, key=lambda v: v["priority"]))
