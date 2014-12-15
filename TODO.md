Important & Critical Items
--------------------------

 - Make the `encode` role actually work(I.E. Encode stuff) - This is kinda done in as much as all the processing is complete for it, it's the script it runs that needs some work.
 - Send process output information back to manager.

General Improvements
--------------------

 - Read this [tutorial](http://krondo.com/?p=2345).

API Improvements
----------------

 - Add a Role implementation which handles enabling and disabling commands when the service is started and stopped given that this is likely to be needed more than once.
 - Remove the need for `lib.monitor.*` as the queues will only run stuff if it is in the directory. - Done, just need to remove the files.
 - Change `roles.encode` to use services to start the processes as opposed to just running them. - This may not be possible. It's probably good as it is.

Production Changes
------------------

 - Change `lib.computer_info` to get the real IP and MAC address.