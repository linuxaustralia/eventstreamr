:mod:`lib.utils` --- Utility classes
####################################

.. contents::


.. module:: eventstreamr2.utils
    :synopsis: General utility classes

Collections
===========

Abstract Classes
----------------

.. currentmodule:: eventstreamr2.utils

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

Concrete Classes
----------------

.. currentmodule:: eventstreamr2.utils

.. autoclass:: PrioritySubDictionary

.. autoclass:: PrioritySubDictionary





Others
======

.. currentmodule:: eventstreamr2.utils

.. autoclass:: Observable

    .. automethod:: add_observer

    .. automethod:: add_weak_observer

    .. automethod:: remove_observer

    .. automethod:: _notify_observers
