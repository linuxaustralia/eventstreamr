:mod:`eventstreamr2.manager` --- Entrypoint for the :term:`Manager`
===================================================================

.. module:: eventstreamr2.manager
    :synopsis: The entrypoint for running the manager.

This module is used when running :program:`twistd`; the program accesses this modules :data:`application` variable; using the :twisted:`application.service.Application` as the root service. All other servies are added as children services to this.

.. warning::
    Do not import manager under any circumstances. It is to be used solely when running the manager through :program:`twistd`.

.. seealso::
    :ref:`tute-running-manager`

.. todo::
    Document this module better.
