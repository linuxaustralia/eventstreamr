__author__ = 'Lee Symes'

import os
import random
import shutil
from uuid import uuid1

from twisted.application.internet import TimerService
from twisted.internet.defer import inlineCallbacks

from eventstreamr2.lib.logging import getLogger
from eventstreamr2.lib import file_helper as files
from eventstreamr2.lib.manager import get_queue_directories
from roles import encode, cut

__current_directories = []

log = getLogger(["queue"])

"""
Should be:
(SendCommand, command_helper, Completed, Failed)
"""
__queue_config = {
    "encode": (encode.StartEncodeRequest, encode.encode_job_manager, encode.EncodeCompleted, encode.EncodeFailed),
    "cut": (cut.StartCutRequest, cut.cut_job_manager, cut.CutCompleted, cut.CutFailed)
}


def create_queue(all_stations, queue_name, base_config, base_dir, file_pattern, poll_length):
    if base_dir in __current_directories:
        raise Exception("Repeated Base Directory")
    queue = Queue(all_stations, base_config, base_dir, poll_length, file_pattern, *__queue_config[queue_name])
    queue.setName(queue_name)
    __current_directories.append(base_dir)
    log.msg("Created Queue %s", queue_name)
    return queue


class Queue(TimerService):

    def __init__(self, all_stations, base_config, base_dir, poll_length, file_pattern,
                 send_command, command_helper, complete_command, failed_command):
        TimerService.__init__(self, poll_length, self.run_poll)
        self.log = log
        self.all_stations = all_stations
        self.base_config = dict(base_config)
        self.base_folder = base_dir
        self.file_pattern = file_pattern
        self.send_command = send_command
        self.complete_command = complete_command
        self.failed_command = failed_command
        self.command_helper = command_helper

    def setName(self, name):
        TimerService.setName(self, name)
        self.log = getLogger(["queue", name])

    def startService(self):
        self.command_helper.responder(self.complete_command)(self.complete)
        self.command_helper.responder(self.failed_command)(self.failed)
        self.command_helper.register()
        TimerService.startService(self)

    def stopService(self):
        self.command_helper.de_register()
        self.command_helper.remove_responder(self.complete_command, self.complete)
        self.command_helper.remove_responder(self.failed_command, self.failed)
        TimerService.startService(self)

    def migrate_file(self, old_file_name, new_file_name, from_folder_type, to_folder_type):  # Helper
        old_file = os.path.join(get_queue_directories(self.base_folder, from_folder_type), old_file_name)
        if not os.path.isfile(old_file):
            log.warning("Failed to locate the original file: %r" % old_file)
            return

        new_folder = get_queue_directories(self.base_folder, to_folder_type)
        if not os.path.isdir(new_folder):
            os.mkdir(new_folder)

        new_file = os.path.join(new_folder, new_file_name)
        shutil.move(old_file, new_file)

    def migrate_file_by_uuid(self, uuid, to_folder_type):
        wip_folder = get_queue_directories(self.base_folder, "wip")
        for file in files.list_files_in(wip_folder, full_path=False):
            if file.startswith(uuid):
                return self.migrate_file(file, file, "wip", to_folder_type)

        raise Exception("UUID(%s) is not found. Here are all the files in the wip folder: %r" %
                        (uuid, files.list_files_in(wip_folder, full_path=False)))

    def complete(self, uuid):
        self.log.msg("Completed running %r inside %r" % (uuid, self.base_folder))
        self.migrate_file_by_uuid(uuid, "done")
        return {}

    def failed(self, uuid, reason):
        self.log.warning("Failed to complete %r inside %r --> Reasons: %r" % (uuid, self.base_folder, reason))
        self.migrate_file_by_uuid(uuid, "fail")
        return {}

    def run_poll(self):
        todo_dir = get_queue_directories(self.base_folder, "todo")
        todo_files = files.list_filtered_files_in(todo_dir, self.file_pattern)

        if not todo_files:
            # Nothing to run so stop right here.
            return

        for file in todo_files:
            self.run_file(file)

    @inlineCallbacks
    def run_file(self, file):
        if not os.path.isfile(file):
            self.log.warning("The following file disappeared out from underneath me: %s" % file)
            return
        config = dict(self.base_config)
        self.log.msg("Base Config: %r" % config)
        c2 = config.update(files.load_json(file))
        self.log.msg("New Config : %r" % config)
        self.log.msg("Config 2   : %r" % c2)
        uuid = str(uuid1())
        new_file = uuid + os.path.basename(file)

        stations = list(self.all_stations.itervalues())
        random.shuffle(stations)

        for station_info in stations:
            if self.name in station_info.station_config.roles:
                print "Checking %r" % station_info.name
                try:
                    res = yield station_info.station_transport.callRemote(self.send_command,
                                                                          job_uuid=uuid,
                                                                          job_config=config)
                except:
                    log.error("Station%r exception whilst starting %r" % (station_info.name, file))
                else:
                    if res["accepted"]:
                        log.msg("Starting to run %r on %r" % (new_file, station_info.name))
                        self.migrate_file(file, new_file, "todo", "wip")
                finally:
                    pass

        pass
