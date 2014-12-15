# General notes #

All configuration items are available to all roles through the configuration manager. This also
means that roles are now responsible for managing updates to their configuration. The configuration
manager is able to fire callbacks when an change to the configuration is made.

# Starting roles #

### Option 1(Roles start at startup) ###

All roles available on the machine are started when the station starts. Then it is up to each role
to maintain itself as configuration items are added and removed.

### Option 2(A Manager handles starting roles) ###

Another service will listen for changes to the configuration and when a new role is detected, it
will start up the role when a configuration for that role appears.

## -- ##

In my opinion, option 1 will be easier to implement, however will make the role implementation
harder.
