from abc import abstractmethod
from collections import Mapping


class Observable(object):
    """

    """

    def __init__(self, *args, **kwargs):
        """

        """
        super(Observable, self).__init__(*args, **kwargs)
        self._observers = list()
        self._weak_observers = list()


    def add_observer(self, fn):
        self._observers.append(fn)


    def remove_observer(self, fn):
        self._observers.remove(fn)


    def _notify_observers(self, *args, **kwargs):
        for fn in self._observers:
            fn(*args, **kwargs)



class AbstractPriorityDictionary(Mapping):
    """
    A dictionary that combines the contents of multiple other dictionaries together; with the value for a key taken from the dictionary that has the highest priority.

    Subclasses simply need to provide an implementation for :meth:`_ordered_configs`.

    .. note::
        This class does no caching; so each call will recalculate the values. This can lead to values changing between calls. Be careful with it.
    """


    def __init__(self):
        super(AbstractPriorityDictionary, self).__init__()


    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.config_manager, self.service_name)


    @abstractmethod
    def _ordered_configs(self):
        """
        This should return an :code:`list(dict)`\(A list containing dictionaries) from
        which the key/value pairs for this dictionary are taken.

        The earlier in the list, the higher priority.
        """
        return []


    def __getitem__(self, key):
        """
        Returns the value for :code:`key` found in the first dictionary or raises a :code:`KeyError`

        :param key: The key to find.

        :raises KeyError: When the key cannot be found.
        """
        cfgs = self.ordered_configs()
        for cfg in cfgs:
            if key in cfg:
                return cfg[key]
        raise KeyError("Missing %r" % key)


    def keys(self):
        """
        Creates a set of all the keys across all the dictionaries.

        .. note::
            Each key will appear exactly once and in an undefined order.

        """
        cfgs = self.ordered_configs()
        keys = set()
        for cfg in cfgs:
            keys.update(cfg.keys())
        return keys


    def __iter__(self):
        """
        Creates an interator over the keys in this dictionary.

        .. seealso::
            :meth:`keys`
        """
        return iter(self.keys())


    def __len__(self):
        """
        The number of unique keys in this dictionary.
        """
        return len(self.keys())


    def __contains__(self, key):
        """
        Searches the database for :code:`key`.
        """
        cfgs = self.ordered_configs()
        for cfg in cfgs:
            if key in cfg:
                return True
        return False


    def all(self, key):
        """
        Returns a list of all the values associated with the key.

        The order of the elements in the returned list is from highest priority(first) to lowest.

        If the key is missing then an empty dictionary is returned.
        """
        values = []
        cfgs = self.ordered_configs()
        for cfg in cfgs:
            if key in cfg:
                values.append(cfg[key])
        return values


    def get_subdictionary(self, key):
        """
        Creates a new :class:`PrioritySubDictionary` that will treat all the values of this key as a priority dictionary.
        """
        return PrioritySubDictionary(self, key)



class PrioritySubDictionary(AbstractPriorityDictionary):
    """
    An implementation of :class:`AbstractPriorityDictionary`.

    This priority dictionary get's it contents from the values of :code:`key` in the parent dictionary provided.
    """


    def __init__(self, parent_dict, key):
        """
        :param AbstractPriorityDictionary parent_dict: The parent dictionary.
        :param key: The key to use.
        """
        super(PrioritySubDictionary, self).__init__()
        self.parent = parent_dict
        self.key = key


    def _ordered_configs(self):
        return self.parent.all(self.key)
