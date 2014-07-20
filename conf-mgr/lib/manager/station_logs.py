__author__ = 'lee'

# TODO Here be the station logging information.

"""

logs/
    023456789AB/                                        #  MAC Address
        encode/                                         #  Role(as handed over(so may not be a role))
            ae7ba221-0fff-11e4-a136-10ddb1a9d409.log    #  Role Specified identifier(uuid of job in encode)
            general.log                                 #  Another log(maybe with start/stop information)
        general.log                                     #  Probably a system log for information.

"""

# So should I have a look at syncing logs for these things.
# Sending/Receiving checksum to ensure that the logs are up to date on the server side.
# Or even the last `n` lines of the station to compare to the last `n` lines in the server's log.
# Or the checksum of the last `n` lines ...