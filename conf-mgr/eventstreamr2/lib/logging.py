#!

"""
This file will contain a lightweight wrapper around :code:`twisted.python.log` to make certain kinds of
logging easier and also allow pre-definition of extra content. This is in preparation for the move
to transmitting station logs to the manager.

This will provide a class that allows:
 - Debug messages that are only output when the :code:`PRODUCTION` environment variable is not set.
 - Simpler logging of error messages
 - The definition of logging location at creation instead of at every log call.

All of these will simply call onto :code:`twisted.python.log` as necessary

It will also be a drop in replace for :code:`from twisted.python import log` by providing a base log
instance which can be imported as: :code:`from eventstreamr2.lib.logging import log` without any code being changed.
"""

from time import strftime, gmtime, time
import string
import random
import sys

_stdout = sys.stdout
_stderr = sys.stderr

from twisted.application.service import Service
from twisted.internet import reactor
from twisted.internet.defer import DeferredList, maybeDeferred, inlineCallbacks
from twisted.python import failure
from twisted.python.log import LogPublisher, textFromEventDict
from twisted.python.logfile import LogFile

from eventstreamr2.lib.computer_info import is_production
from eventstreamr2.lib.commands import configuration_helper
import eventstreamr2.lib.amp.arguments as amp
from eventstreamr2.lib.file_helper import list_filtered_files_in, exists, join, read_in, delete
_logging_commands = configuration_helper("Station Logging")

@_logging_commands.command
class SendLogsCommand(amp.Command):
    """

    """
    arguments = [("logs", amp.Object()),
                 ("transport", amp.Transport())]
    response = [("accepted", amp.Boolean())]


class Logger(LogPublisher):
    """
    Logger.
    """

    def __init__(self, location=("general",), transmit=False):
        self.location = location
        self.transmit = transmit
        LogPublisher.__init__(self)

    def debug(self, *message, **kw):
        kw["isDebug"] = True
        self.msg(*message, **kw)

    def cmd_output_stderr(self, output):
        self.cmd_output("ERR", output)

    def cmd_output_stdout(self, output):
        self.cmd_output("OUT", output)

    def cmd_output(self, prefix, output):
        self.msg("\n".join([prefix + "| " + line for line in output.splitlines()]))

    def msg(self, *message, **kw):
        kw.setdefault("location", self.location)
        kw.setdefault("transmit", self.transmit)
        LogPublisher.msg(self, *message, **kw)

    def error(self, message, **kw):
        self.msg(message, failure=failure.Failure(), isError=1, **kw)

    def warning(self, message, **kw):
        self.msg(message, isError=1, **kw)

    def err(self, _stuff=None, _why=None, **kw):
        """
        Write a failure to the log.

        The :code:`_stuff` and :code:`_why` parameters use an underscore prefix to lessen
        the chance of colliding with a keyword argument the application wishes
        to pass.  It is intended that they be supplied with arguments passed
        positionally, not by keyword.

        @param _stuff: The failure to log.  If :code:`_stuff` is :code:`None` a new
            L{Failure<twisted.python.failure.Failure>} will be created from the current exception
            state.  If :code:`_stuff` is an :code:`Exception` instance it will be wrapped in a
            :code:`Failure`.
        @type _stuff: :code:`NoneType`, :code:`Exception`, or L{Failure<twisted.python.failure.Failure>}.

        @param _why: The source of this failure.  This will be logged along with
            :code:`_stuff` and should describe the context in which the failure
            occurred.
        @type _why: :code:`str`
        """
        if _stuff is None:
            _stuff = failure.Failure()
        if isinstance(_stuff, failure.Failure):
            self.msg(failure=_stuff, why=_why, isError=1, **kw)
        elif isinstance(_stuff, Exception):
            self.msg(failure=failure.Failure(_stuff), why=_why, isError=1, **kw)
        else:
            self.msg(repr(_stuff), why=_why, isError=1, **kw)


class LogTransmissionService(Service):
    """
    Transmission Service.
    """


    def __init__(self, ):
        self.__temporary_log_location = "logs-temp/"
        self.__extension = "-tmp.log"
        self.__remote_connection = None
        self.__current_file = None
        self.__current_fd = None
        self.pending = None

    @property
    def remote_connection(self):
        return self.__remote_connection

    @remote_connection.setter
    def remote_connection(self, new_connection):
        if self.running:
            # TODO safely restart the service with new connection.
            raise Exception("Running")
        else:
            self.__remote_connection = new_connection
            if new_connection:
                # I've got a new connection so schedule the sending of all the logs.
                schedule_pending(now=True)

    @property
    def current_fd(self):
        if self.__current_fd is None or self.__current_fd.closed:
            if self.__current_file is None:
                self.rotate(None)
            else:
                self.__current_fd = open(self.__current_file, "wa")
        return self.__current_fd

    @property
    def extension(self):
        return self.__extension

    @extension.setter
    def extension(self, extension):
        if self.running:
            raise Exception("Running")
        else:
            self.__extension = extension

    @property
    def temporary_log_location(self):
        return self.__temporary_log_location

    @temporary_log_location.setter
    def temporary_log_location(self, new_location):
        if self.running:
            raise Exception("Service is running so I can't change the location. Please stop the"
                            " service before changing the location")
        else:
            self.__temporary_log_location = new_location

    def startService(self):
        Service.startService(self)
        return self.send_logs()

    def stopService(self):
        Service.stopService(self)
        return self.send_logs()

    def write_entry(self, location, log_time, entry):
        location_string = "|".join(location)
        self.current_fd.write("%f:%s:%s\0" %
                                (log_time, location_string, entry.replace("\0", "\\0")))
        self.current_fd.flush()
        self.schedule_pending()

    def schedule_pending(self, now=False):
        if not self.pending or not self.pending.active():
            if now:
                self.pending = reactor.callLater(0, self.do_pending)
            else:
                self.pending = reactor.callLater(random.uniform(2, 10), self.do_pending)
        elif now:
            # Reschedule the call to ASAP.
            self.pending.reset(0)

    def do_pending(self):
        self.pending = None
        try:
            self.send_logs()
        except:
            self.schedule_pending()
            raise

    def send_logs(self):
        lst = []
        for file in list_filtered_files_in(self.temporary_log_location, "*" + self.extension):
            lst.append(maybeDeferred(self.send_log, file))
        return DeferredList(lst)

    @inlineCallbacks
    def send_log(self, queue_file):
        if not self.remote_connection:
            # Can't send the logs without somewhere to send them.
            return
        self.rotate(queue_file)
        queue_content = read_in(queue_file)
        log_entries = []
        for entry in queue_content.split("\0"):
            if not entry: # Is empty
                continue
            time, location_as_string, msg = entry.split(":", 2)  # 2 splits to give 3 elements
            location = tuple(location_as_string.split("|"))
            log_entries.append((float(time), location, msg))
        try:
            result = yield self.remote_connection.callRemote(SendLogsCommand, logs=log_entries)
            if result["accepted"]:
                delete(queue_file)
        except:
            log.error("Failed to transmit information contained in %s. "
                      "This may be due to a disconnecting client." % queue_file)
            raise

    def rotate(self, file=None):
        if self.__current_file != file:
            return
        else:
            import os
            dt = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
            folder = os.path.abspath(self.temporary_log_location) + os.sep
            if not os.path.exists(folder):
                os.makedirs(folder)
            f = join(self.temporary_log_location, dt + self.extension)
            if not exists(f):
                self.__current_file = f
                self.__current_fd = open(f, "w")
            else:
                raise Exception("The file(%s) already exists. This should never occour" % f)


class LogObserver(object):

    def __init__(self, service, folder="logs/", extension=".log"):
        self.service = service
        self.folder = folder
        self.extension = extension

    def emmit(self, event):
        if event.get("isDebug", False) and is_production():
            return  # Don't log debug messages in production.
        location, prefix, log_time, log_time_str, entry_text = self.parse_from(event)
        folder, name = build_file(self.folder, location, self.extension)
        try:
            log = LogFile(name, folder)
            log.write("%s %s\n\t%s\n" % (prefix, log_time_str, entry_text.replace("\n", "\n\t\t")))
            log.flush()
            log.close()
        finally:
            if event.get("transmit", False) and not event.get("isDebug", False):
                self.service.write_entry(location, log_time, entry_text)

    def parse_from(self, event):
        location = event.get("location", [])
        if not location:
            location = ["general"]
        log_time = event.get("time", time())
        log_time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime(log_time))
        entry_text = textFromEventDict(event)
        prefix = "MSG"
        if event.get("isError", False):
            prefix = "ERR"
        if event.get("isDebug", False):
            prefix = "DBG"
        return location, prefix, log_time, log_time_str, entry_text

    def print_to_sys(self, event):
        location, prefix, log_time, log_time_str, entry_text = self.parse_from(event)

        out = _stdout
        if event.get("isError", False):
            out = _stderr

        lines = (["%s %s -> %s\n" % (prefix, log_time_str, ">".join(location))] +
                ["\t|%s\t%s\n" % (prefix, l) for l in entry_text.splitlines()])

        out.writelines(lines)
        out.flush()



def build_file(folder, paths, extension):
    import os
    folder = os.path.abspath(folder)
    for path in paths[:-1]: # All except the last one
        check_path(path)
        folder = os.path.join(folder, path + os.path.sep)
    if not os.path.exists(folder):
        os.makedirs(folder)
    if len(paths) < 1:
        raise Exception("Must specify a path.")
    check_path(paths[-1])
    return folder, paths[-1] + extension


accepted_chars = string.ascii_letters + string.digits + '-_'
def check_path(path):
    """

    :param path:
    :type path: string
    :return:
    :rtype:
    """
    if path.translate(None, accepted_chars):  # Has any non-allowed chars
        raise Exception("Invalid path %r" % path)


def emmit(event):
    observer.emmit(event)

def emmit_to_term(event):
    observer.print_to_sys(event)

def getLogger(location, _transmit=None):
    if _transmit is None:
        _transmit = transmit
    loc = [str(e) for e in location]
    l = Logger(location=loc, transmit=_transmit)
    l.addObserver(emmit)
    l.addObserver(emmit_to_term)
    return l

# Allow global configuration of transmission.
transmit = True

# Default - Don't transmit it.
log = Logger(transmit=False)
transmit_service = LogTransmissionService()
observer = LogObserver(transmit_service)

if __name__ == "__main__":
    getLogger(["general"]).msg("Hello World")
