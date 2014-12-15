from __future__ import absolute_import

import collections

from abc import abstractmethod
from collections import Mapping, Sized, Container, Iterable
from functools import partial
import weakref


class WeakFunctionCollection(Iterable):

    def __init__(self):
        self._container = []

    def __iter__(self):
        for obj, fn in list(self._container):
            if obj is None:
                # Unbound
                f = fn() # Deref.
                if f is None:
                    self._container.remove((obj, fn))
                else:
                    yield f
            else:
                # Bound
                fn_self = obj() # Deref
                if fn_self is None:
                    self._container.remove((obj, fn))
                else:
                    yield partial(fn, fn_self)


    def append(self, fn):
        if hasattr(fn, '__self__'):
            # Bound so we need to do some funky stuff
            s = getattr(fn, '__self__')
            f = getattr(fn, '__func__')

            self._container.append((weakref.ref(s), f))
        else:
            self._container.append((None, weakref.ref(fn)))



class WeakCollection(Sized, Container, Iterable):
    """
    Order is not maintained. Multiple elements are supported.
    """


    def __init__(self, lst=[]):
        self._counter = 0
        self._container = weakref.WeakValueDictionary()
        self.append(*lst)


    def __contains__(self, other):
        # TODO change this to be python 3 compatable.
        return other in self._container.values()


    def __iter__(self):
        return self._container.itervalues()


    def __len__(self):
        return len(self._container)


    def append(self, *items):
        for item in items:
            self._container[self._counter] = item
            self._counter += 1


    def remove(self, *items):
        """
        Remove the first occourance of each argument.
        """
        for item in items:
            for k, v in list(self._container.items()):
                if v == item:
                    del self._container[k]
                    break


    def removeAll(self, *items):
        """
        Removes all ocourances of each argument.
        """
        for item in items:
            for k, v in list(self._container.items()):
                if v == item:
                    self._container.pop(k, None)



class AbstractPriorityDictionary(Mapping):
    """
    An immutable dictionary that combines the contents of multiple other dictionaries together; with the value for a key taken from the dictionary that has the highest priority.

    Subclasses simply need to provide an implementation for :meth:`_ordered_configs`.

    This is an example to show how this method resolves keys::

        >>> class APD(AbstractPriorityDictionary):
        ...     def _ordered_configs(self):
        ...         return [
        ...             {"a": 1, "b": 1.2},
        ...             {        "b": 2.2, "d": 2.4, "z", {"a": 1}},
        ...             {"a": 3,           "e": 3.4, "z", {"a": 2}},
        ...         ]
        ...
        >>> c = APD()
        >>> c["a"]
        1
        >>> c.get("d")
        3.5
        >>> c["f"]
        KeyError
        >>> c.get("f", "default")
        "default"
        >>> c.all("a")
        [1, 3]
        >>> c.all("f")
        []
        >>> c.get_subdictionary("z").all("a")
        [1, 2]

    .. note::
        This class does no caching; so each call will recalculate the values. This can lead to values changing between calls. Be careful with it.
    """


    def __init__(self):
        super(AbstractPriorityDictionary, self).__init__()


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
        cfgs = self._ordered_configs()
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
        cfgs = self._ordered_configs()
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
        # TODO Rewrite this to use yield.
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
        cfgs = self._ordered_configs()
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
        cfgs = self._ordered_configs()
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
