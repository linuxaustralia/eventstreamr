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

from time import strftime, gmtime

from twisted.application.service import Service
from twisted.python.logfile import LogFile

from eventstreamr2.lib.logging import SendLogsCommand, _logging_commands, build_file


class StationLogReceiver(Service):

    def __init__(self, stations, output_folder="station-logs/", extension=".log"):
        self.__output_folder = output_folder
        self.__extension = extension
        self.__stations = stations

    def startService(self):
        _logging_commands.responder(SendLogsCommand, self.receive_logs)
        _logging_commands.register()
        Service.startService(self)

    def stopService(self):
        _logging_commands.remove_responder(SendLogsCommand, self.receive_logs)

    def receive_logs(self, logs, transport):
        client_mac = self.__stations[transport.client].mac;
        client_mac = client_mac.translate(None, ":|/\\")
        files = {}
        for time, location, msg in logs:
            if location in files:
                log_file = files[location]
            else:
                loc = [client_mac] + list(location)
                folder, name = build_file(self.__output_folder, loc, self.__extension)
                log_file = LogFile(name, folder)
                files[location] = log_file
            log_time_str = strftime("%Y-%m-%d %H:%M:%S:%f", gmtime(time))
            log_file.write(">%s\n\t%s\n" % (log_time_str, msg.replace("\n", "\n\t\t")))

        # Now close those files
        for log_file in files.itervalues():
            log_file.flush()
            log_file.close()
        return {"accepted": True}
