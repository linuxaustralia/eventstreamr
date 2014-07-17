__author__ = 'Lee Symes'

import random
import shutil
import os

from twisted.internet.defer import returnValue, inlineCallbacks

from uuid import uuid1
from lib import file_helper as files
from lib.manager import get_queue_directories
from roles.encode import StartEncodeRequest, EncodeCompleted, EncodeFailed, _encode_job_manager

class EncoderQueue(object):

    def __init__(self, config, all_stations):
        ":type all_stations: dict[tuple[string,int], manager.StationInformation]"
        self.all_stations = all_stations
        self.config = config
        self.folder = config["base_path"]
        self.jobs = {}
        print "Initilising Encoder Queue --> ", self.config
        _encode_job_manager.responder(EncodeCompleted)(self.completed)
        _encode_job_manager.responder(EncodeFailed)(self.failed)
        _encode_job_manager.register()

    def completed(self, uuid):
        print "Completed " + uuid
        self.migrate_file(uuid, "done")
        del self.jobs[uuid]
        return {}

    def failed(self, uuid, failure_information):
        print "Failed" + uuid
        print "\t\t", failure_information
        self.migrate_file(uuid, "fail")
        del self.jobs[uuid]
        return {}

    def migrate_file(self, uuid, folder_type):
        old_file = self.jobs[uuid]
        new_folder = get_queue_directories(self.folder, folder_type)
        if not os.path.isdir(new_folder):
            os.mkdir(new_folder)

        new_file = os.path.join(new_folder, os.path.basename(old_file))
        shutil.move(old_file, new_file)


    @inlineCallbacks
    def __call__(self):
        todo_folder = get_queue_directories(self.folder, "todo")
        todo_files = files.list_filtered_files_in(todo_folder,
                                                  self.config["file_pattern"])
        wip_folder = get_queue_directories(self.folder, "wip")
        if not os.path.isdir(wip_folder):
            os.mkdir(wip_folder)

        for file in todo_files:
            uuid = yield self.call_for_file(file)
            print "Tried to run", file, " - The UUID returned was: ", uuid
            if uuid:
                wip_file = os.path.join(wip_folder, uuid + "_" + os.path.basename(file))
                shutil.move(file, wip_file)
                self.jobs[uuid] = wip_file
            else:
                print "Failed to start " + file
                print "Will reattempt later."
        
        print "WIP Files:"
        print "\n\t\t".join(files.list_files_in(wip_folder))

    @inlineCallbacks
    def call_for_file(self, file):
        content = files.read_in(file)
        # Replace this with actual codes.
        print "Running " + file
        print "Running " + content
        input_files = [("Input 1", 1, 2), ("Input 2", 0, 100)]
        output_file = "Old Name: " + file
        uuid = str(uuid1())
        stations = list(self.all_stations.itervalues())

        for station_info in random.sample(stations, len(stations)):
            print "Loading up station: ", station_info
            if station_info.station_config.roles.has_key("encode"):
                print "Found an encoder, trying it."
                transport = station_info.station_transport
                res = yield transport.callRemote(StartEncodeRequest,
                                                 job_uuid=uuid,
                                                 input_files_and_cutoffs=input_files,
                                                 output_file=output_file)
                print "Responded", res
                if res:
                    returnValue(uuid)
        print "Nothing found."
        returnValue(None)



