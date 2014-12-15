
Executing Processes
###################

All commands should be executed asynchronusly. There are 3 basic methods to do this.

.. note::

    All these are assumed to be run from within a :class:`InternalServiceMixin`. This means that calls to the reactor will use :code:`self._reactor` and constructing further internal servic

.. _executing-run-once:

Run once
========

To run a command once use::

    self._reactor.spawnProcess(protocol, executable, args);

(see :twisted:`spawnProcess <twisted.internet.interfaces.IReactorProcess.spawnProcess>`)This will spawn a process using a ProcessProtocol(:code:`protocol`). Executing the :code:`executable` with :code:`args` as the arguments. It is conventional to place the excecutable as the first argument.

To write a ProcessProtocol, see :ref:`writing-process-protocol`.


.. _executing-keep-running:

Keep a program open
===================

Use this to keep a program running::

    from eventstreamr2.lib.amp.service import ProgramExecutionService

    service = self._init_new_service(ProgramExecutionService, program_and_args)
    service.setParent(self).

The :code:`program_and_args` should have the program to execute as the first element and then the arguments following.

Example
-------

::

    class DVSwitchService(InternalServiceMixin, Service):

        def __init__(self, **kwargs):
            super(DVSwitchService, self).__init__(self, **kwargs)
            pes = self._init_new_service(ProgramExecutionService, ["dvswitch"])
            pes.setParent(self)

In this example, The service simply acts as a wrapper around the :code:`ProgramExecutionService`








.. _writing-process-protocol:

Writing a Process Protocol
==========================

Write code - get results.
