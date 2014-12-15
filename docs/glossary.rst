:orphan:

.. _glossary:

********
Glossary
********

.. glossary::
    :sorted:

    Manager
        The 'server' from which the :term:`stations <Station>` are controlled. This runs a subset of roles and is intended to be lightweight and easily configurable.

    Role
        A :term:`Twisted service` that is responsible for managing a small aspect of functionality.
        For example an encoding role has the sole purpose of recieving and runing an encode job.

    Station
        The 'child' on which most processing is done. It runs most of the :term:`roles <Role>`
