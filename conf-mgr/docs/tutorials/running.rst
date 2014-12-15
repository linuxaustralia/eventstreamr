.. _tutorials-running:

Running the Service
*******************


.. _twistd-command:

The :program:`twistd` Command
=============================

.. program:: twistd

Twisted provides a utility - :program:`twistd` - which allows any twisted program to be run as a
service. The program handles starting and stopping as well as many other options. The most
important are documented below; with the full listing available on
`twistd's man page <http://manpages.ubuntu.com/manpages/trusty/man1/twistd.1.html>`_

.. option:: -n, --nodaemon

    Force :program:`twistd` to run in the foreground.

.. option:: --pidfile <pidfile>

    Outputs the PID of the process to this file. The default file is :file:`twistd.pid`

.. option:: -d, --rundir <directory>

    Use this to define the directory to run out off. Note that this should be specified when :program:`twistd` is run using root and the program is not in the python path(When running as root, the current directory is not included in the python path).

.. option:: -y, --python <python file>

    Indicates that the :code:`application` variable should be taken from the python file(once it is
    imported) and used as the root service.


.. _tute-running-manager:

Running the Manager
===================

The following command will run the manager in the foreground.

.. code-block:: console

    $ twistd --pidfile manager.pid --nodaemon --python manager.py

Remove the :option:`--nodaemon` option to daemonise the service. Then to kill the daemonised manager run:

.. code-block:: console

    $ kill `cat manager.pid`
