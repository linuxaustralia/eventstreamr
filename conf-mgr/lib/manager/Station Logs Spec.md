So I'm thinking that if I create a service which can just receive the logs and save them to a file specified by the server(inside a folder of the MAC Address(or hostname or IP)).
I'm going to implement it in [/conf-mgr/lib/manager/station_logs.py](https://github.com/leesdolphin/eventstreamr/blob/master/conf-mgr/lib/manager/station_logs.py).

I'm laying the folder out like:

    logs/
        0123456789AB/                                       #  MAC Address
            encode/                                         #  Role(as handed over(so may not be a role))
                ae7ba221-0fff-11e4-a136-10ddb1a9d409.log    #  Role Specified identifier(uuid of job in encode)
                general.log                                 #  Another log(maybe with start/stop information)
            general.log                                     #  Probably a system log for information.

I'm going to layout the posting of logs like so:

**Communication:** Station -> Manager
**Sent Information:**

    log_location (Object) -> ["encode", "general"]
            # This would output to the `logs/0123456789AB/encode/general.log`
    log_data (BigUnicode) -> "<<Raw Log Output Here>>"
    update_time (Integer) -> <<Milliseconds since epoch>>

**Received Information:**

    written (Boolean) -> True
            # Just to be sure; This is so that the station can now move that information into a `sent` log file.

The benefit with responding with `written` is that the station guarantees that the manager has the logs prior to removing them; Whilst this could cause duplication of some lines in the log files contained on the manager, the manager would not be missing any log lines.

Side Note: Should write out to the station's log file when the log entry is received not when it is confirmed. This will make the logs on the station the authoritative logs with the ones on the manager being a very close second(hopefully just with duplicated lines(not missing)).

Things To Do
------------

 - Write a basic receiver that is able to handle receiving and writing the logs out to the correct files. I would have to worry about the number of file descriptors so probably opening with `open(name, 'w+')` then closing once completed writing that block.

 - Probably write a `twisted.python.log` handler that deals with receiving them and sending them off to the network and to a temporary log. Once the information has been confirmed that it is received; clear out the sent stuff and move it into the real log(or a similar log layout to the above).

 - Write a startup handler that sends any temporary logs off to the manager when the station starts up.
    - Or simply have the handler detect that the file isn't empty so it should queue it for transmission and not use it as it's temporary log file.

 - Figure out how to do no.2 whilst keeping the `log_location` information.

    - **Cunning Plan:** Change the sent information to be a list of log entries with a tuple containing 
      
      ```
      (log_location, log_data, update_time)
      ```
      
      Or more fully:
      **Sent Information:**
      
      ```
      logs (Object) -> [(["encode", "general"], "<<Raw Log Entry Here>>", <<Millis>>), ...]
      ```
      
      Once the station receives the response, it can just clear or delete the file and switch over to the other one. This could mean that this simply runs as a polling job where it switches the log files and sends them every minute. And then add an extra handle so if a major error occurs the logs are sent.
