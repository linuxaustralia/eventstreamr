from collections import OrderedDict
from lib.logging import getLogger
from twisted.application.service import MultiService

_log = getLogger(("lib", "configuratuion", "__init__"))


class ConfigurationManager(MultiService):

  def __init__(self):
    self.configs = {}

  def __str__(self):
    import json
    return json.dumps(self.configs, indent=4)

  def __repr__(self):
    return "%s(%s)" % (self.__class__.__name__, str(self))

  def set_config(self, service_name, source_name, source_priority, new_config):
    self.configs.setdefault(service_name, {}) # Setup service name
    self.configs[service_name][source_name] = {"priority": source_priority,
                                               "config": new_config}

  def get_config(self, service_name):
    return ServiceConfigurationWrapper(self, service_name)

  def delete_config(self, service_name, source_name=None):
    if service_name in self.configs:
      if source_name is not None:
        self.configs[service_name].pop(source_name, None)
      else:
        self.configs.pop(service_name)
    return None


class ServiceConfigurationWrapper(object):

  def __init__(self, config_manager, service_name):
    self.config_manager = config_manager
    self.service_name = service_name

  def __repr__(self):
    return "%s(%r, %r)" % (self.__class__.__name__, self.config_manager, self.service_name)

  def service_config(self):
    return self.config_manager.configs.get(self.service_name, {})

  def ordered_configs(self):
    return map(lambda v: v["config"],
               sorted(self.service_config().values(), reverse=True, key=lambda v: v["priority"]))

  def get(self, key, default=None):
    cfgs = self.ordered_configs()
    for cfg in cfgs:
      if key in cfg:
        return cfg[key]
    return default

  def __getitem__(self, key):
    cfgs = self.ordered_configs()
    for cfg in cfgs:
      if key in cfg:
        return cfg[key]
    raise KeyError("Missing %r" % key)

  def keys(self):
    cfgs = self.ordered_configs()
    keys = set()
    for cfg in cfgs:
      keys.update(cfg.keys())
    return keys

  def __iter__(self):
    return iter(self.keys())

  def __len__(self):
    return len(self.keys())

  def __contains__(self, key):
    cfgs = self.ordered_configs()
    for cfg in cfgs:
      if key in cfg:
        return True
    return False

  def all(self, key):
    values = []
    cfgs = self.ordered_configs()
    for cfg in cfgs:
      if key in cfg:
        values.append(cfg[key])
    return values
