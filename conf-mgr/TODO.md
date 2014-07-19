Important & Critical Items
--------------------------

 - Migrate Manager to a `twistd` architecture as explain in the [Twisted docs](http://twistedmatrix.com/documents/current/core/howto/application.html) and this [tutorial](http://krondo.com/?p=2345)
    - This includes reworking `lib.manager.queue.EncoderQueue` to be a service.
 - Make the `encode` role actually work(I.E. Encode stuff)

General Improvements
--------------------

 -

API Improvements
----------------

 - Change `lib.commands._ConfigurationHelper.responder` to accept 2 arguments so that `_.responder(command, callback)` is a valid function call.
 - Add a Role implementation which handles enabling and disabling commands when the service is started and stopped given that this is likely to be needed more than once.
 - Remove the need for `lib.monitor.*` as the queues will only run stuff if it is in the directory.
 - Change `roles.encode` to use services to start the processes as opposed to just running them.
 - Chang `roles.Role` to implement `MultiService` as it has no difference on implementers other than an easier way to add/remove sub-services(which is nice).

Production Changes
------------------

 - Change `lib.computer_info` to get the real IP and MAC address.
 -