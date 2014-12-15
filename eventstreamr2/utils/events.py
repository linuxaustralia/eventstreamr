from eventstreamr2.utils.collections import WeakFunctionCollection


class Observable(object):
    """
    An mixin object that provides an event listener style interface.

    .. note::
        It is reccomended that :meth:`add_weak_observer` is used whenever possible as it handles
        cleanup better than it's strong counterpart.

    .. note::
        :code:`remove_weak_observer` is missing intentionally; Primarily because it is unlikely to
        be needed; and secondly because it is hard to implement a remove method inside
        :class:`WeakFunctionCollection`.
    """

    def __init__(self, *args, **kwargs):
        """
        Setup the observable. All arguments are passed on to a super call.
        """
        super(Observable, self).__init__(*args, **kwargs)
        self._observers = list()
        self._weak_observers = WeakFunctionCollection()


    def add_observer(self, fn):
        """
        Add an observer function.
        """
        self._observers.append(fn)


    def add_weak_observer(self, fn):
        """
        Add an observer function that is stored weakly. This means that when the given function
        leaves scope, it will no longer be called. Special handling is done on bound methods to
        ensure that they are not removed until the object they are bound on leaves scope.
        """
        self._weak_observers.append(fn)


    def remove_observer(self, fn):
        """
        Remove an observer function.
        """
        self._observers.remove(fn)


    def _notify_observers(self, *args, **kwargs):
        """
        Notify all existing observers, or more specifically call each observer with any
        arguments(both positional and keyword) passed in.

        All listeners defined at the start of this method's execution will be called and any
        changes afterwards will not affect this method call.
        """
        # The weak functions won't be garbage collected because they are saved in the list below.
        # This makes the
        listeners = list(self._observers) + list(self._weak_observers)
        for fn in listeners:
            fn(*args, **kwargs)
