from abc import abstractmethod
from collections import Mapping


class Observable(object):

  def __init__(self, *args, **kwargs):
    super(Observable, self).__init__(*args, **kwargs)
    self._observers = list()

  def add_observer(self, fn):
    self._observers.append(fn)

  def remove_observer(self, fn):
    self._observers.remove(fn)

  def _notify_observers(self, *args, **kwargs):
    for fn in self._observers:
      fn(*args, **kwargs)


class AbstractPriorityDictionary(Mapping):

    def __init__(self):
        super(AbstractPriorityDictionary, self).__init__()

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.config_manager, self.service_name)

    @abstractmethod
    def ordered_configs(self):
        """
        This should return an C{list}-like object containing C{dict}-like objects from which the
        key/value pairs for this dictionary are taken.

        The earlier in the list, the higher priority.
        """
        return []

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


class PrioritySubDictionary(AbstractPriorityDictionary):

    def __init__(self, parent_dict, key):
        super(PrioritySubDictionary, self).__init__()
        self.parent = parent_dict
        self.key = key

    def ordered_configs(self):
        return self.parent.all(self.key)
