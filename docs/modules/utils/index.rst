:mod:`eventstreamr2.utils` --- Utilities
########################################

.. contents::


.. module:: eventstreamr2.utils
    :synopsis: Utility classes.

:mod:`eventstreamr2.utils.collections`
======================================

.. module:: eventstreamr2.utils.collections
    :synopsis: Collections including a weak list that supports bound functions.

Concrete Classes
----------------

.. autoclass:: PrioritySubDictionary


.. autoclass:: WeakCollection
    :members:

.. autoclass:: WeakFunctionCollection
    :members:


Abstract Classes
----------------

.. autoclass:: AbstractPriorityDictionary

    .. seealso::
        This module includes :class:`collections.Mapping` and this provides additional
        functionality.

    .. automethod:: _ordered_configs

        .. note:: Only this method needs to be implemented.

    .. automethod:: get

    .. automethod:: all

    .. automethod:: keys

    .. automethod:: items

    .. automethod:: values

    .. automethod:: __getitem__

    .. automethod:: __iter__

    .. automethod:: __len__

    .. automethod:: __contains__



:mod:`eventstreamr2.utils.events`
=================================

.. currentmodule:: eventstreamr2.utils.events

.. autoclass:: Observable

    .. automethod:: add_observer

    .. automethod:: add_weak_observer

    .. automethod:: remove_observer

    .. automethod:: _notify_observers
