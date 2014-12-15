:mod:`lib.utils` --- Utility classes
====================================

.. module:: lib.utils
    :synopsis: General utility classes


Concrete Classes
----------------

.. currentmodule:: lib.utils

.. autoclass:: PrioritySubDictionary



Abstract Classes
----------------

.. currentmodule:: lib.utils

.. autoclass:: Observable

    .. automethod:: add_observer

    .. automethod:: remove_observer

    .. automethod:: _notify_observers


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

    .. automethod:: __eq__

    .. automethod:: __ne__
