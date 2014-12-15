Conference Manager
================== 

[![Documentation Status](https://readthedocs.org/projects/eventstreamr/badge/?version=latest)](https://readthedocs.org/projects/eventstreamr/?badge=latest)

This project aims to reimplement the EventStreamr in Python.

This project currently has the following dependencies:

 - Commands: `ifdata` and `hostname`
 - Python 2.7.8
 - PIP packages:
   - `Twisted` (currently version 14.0.0)

This may also require PIP packages `pyOpenSSL` and `service_identity` if SSL is required. Otherwise it produces the following warning:
`UserWarning: You do not have the service_identity module installed. Please install it...`



Running the files
-----------------

To run the manager, simply execute `python -m manager`

To run the station, simply execute `twistd --nodaemon --python station.py` or for daemon mode: `twistd --python station.py`.
For more information on daemon mode and `twistd`, see the [Twisted Documentation](http://twistedmatrix.com/documents/current/core/howto/basics.html)

Configuration Files
-------------------

###manager.json

###station.json

###station_config.json

These are laid out as mappings from a role to a uuid to the configuration. as:

    //  <Role>      <UUID>          <Config Options>
    {
        "encode": {
                    "uuid - 1": {
                                    "timestamp": 100,
                                    "script": "hello_world.py"
                    },
        "upload": {
                    "uuid - 1": {
                                    "timestamp": 100,
                                    "script": "upload_to_youtube.py"
                    }
        }
    }


Manager/Station Communication
-----------------------------

The following assumes that the manager is currently running and that the station is able to communicate with the manager.

 1. The station connects to the manager.
 2. The station sends it's current configuration which includes IP(though not required), hostname, MAC address and currently configured roles(Using `lib.general_commands.RegisterStationCommand`). This request isn't responded to in any order.
 3. The manager sends a(separate) request to the station with the up to date role config(may be the same as sent in step 2)(Using `lib.config.UpdateConfiguration`).
 4. The station responds to the request in step 3 to indicate if the configuration was successful. This is indicated by no exception being thrown. If the configuration is invalid then one of `InvalidConfigurationException`, `MissingRoleFactoryException` or `BlockedRoleException`(all from `lib.exceptions`) is thrown with a descriptive error message. This message is enough to determine the problem without having to access the station's logs.

Using this mechanism of the manager notifying the station of updates will reduce polling for updates and disconnects the 'Hello' request from updating the role's configurations.
