.. _tutorials-new_role:

Creating a new Role
===================

All non-core code is contained in a role. Each role has one specific purpose, be that to monitor the video streams or run encoding jobs.

.. _new_role-file_setup:
Creating and seting up the file
-------------------------------

The first step in creating a new role is to create a file inside the :file:`roles` package. All modules in this package(including subpackages) will be included when the system starts up.

Now simply create a new :class:`lib.roles.Role` class
