:mod:`lib.utils`
======================================================

.. module:: lib.utils
    :synopsis: General utility classes


Concrete Classes
----------------

.. currentmodule:: lib.utils

.. autoclass:: PrioritySubDictionary
    :members:
    :undoc-members:
    :show-inheritance:


Abstract Classes
----------------

.. currentmodule:: lib.utils

.. autoclass:: Observable
    :members: add_observer, remove_observer, _notify_observers
    :undoc-members:

.. autoclass:: AbstractPriorityDictionary

    .. seealso::
        This module includes :class:`collections.Mapping` and this provides additional
        functionality.

    .. todo::
        Documenting this.

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
