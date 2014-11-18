
from lib.logging import getLogger
from twisted.application.service import MultiService

log = getLogger(("manager", ), False)


__config_classes = {};

def service_config(config_name, cfg_class=None):
  if not isinstance(config_name, basestring):
    raise ValueError("Incorrect call")
  def configure(config_class):
    if config_name in __config_classes:
      raise ValueError("Duplicate registration")
    # TODO: Confirm that the class is of the correct type.
    __config_classes[class_name] = config_class
    return config_class
  if cfg_class is not None:
    return configure(cfg_class)
  else return configure


class ConfigManager(MultiService):

  def __init__(self):
    self.__configs = {}
    pass

  def update_configs(self, service_name, new_config, default=False):
    if service_name not in __config_classes:
      raise ValueError("That service is not regisered. Ensure that your module is imported")
    else if service_name not in self.__configs:
      new_config = __config_classes[service_name]()
      self.__configs[service_name] = new_config

    self.__configs[service_name].update_configs(new_config, default=default);

  def get_config(self, service_name):
    if service_name not in self.__configs:
      return None
    else:
      return self.__configs[service_name]

  def delete_config(self, service_name):
      if service_name not in self.__configs:
        return None
      else:
        old_service = self.__configs.pop(service_name, None)
        if old_service is not None:
          old_service.deactivate()
          return True
        return None





class ConfigurationStore(object):

  def __init__(self):
    super(ConfigurationStore, self).__init__()

  def update_configs(self, new_config, default=False):
    # Default No-op
    pass

  def deactivate(self):
    # Also No-op
    pass
