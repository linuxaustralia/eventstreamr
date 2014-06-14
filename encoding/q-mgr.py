#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json
import datetime
import os
import subprocess

from lib.schedule import *
from lib.ui import *
from lib.duration import *
from lib.job import *

# Main Constants
config_file = "config.json"

# read the config file
config_data = open_json(config_file)

# should be referencing config data directly
base_dir = config_data['base_dir']
schedule_file = base_dir + "/" + config_data['schedule']
recording_dir = base_dir + "/recording"
queue_todo_dir = base_dir + "/queue/todo"
completed_dir = base_dir + "/completed"

json_format="%Y-%m-%d %H:%M:%S"

dv_format="%Y-%m-%d_%H-%M-%S"
dv_match_window = datetime.timedelta(minutes=10)

# first pass through the recording directory: find the times of all .dv files
talks = get_schedule(schedule_file, json_format)
for talk in talks:
    link_dv_files(talk, recording_dir, dv_match_window, dv_format)

jobs = { t['schedule_id']: t for t in talks if t["playlist"] }

print "Available jobs:", [t for t,v in jobs.items() if v["playlist"]]
n = prompt_for_number("Select a job")

while n: 
    talk = jobs[n]

    dvfiles = [z["filepath"] + "/" + z["filename"] for z in talk["playlist"]]

    DEVNULL = open(os.devnull, 'wb')
    subprocess.Popen(["vlc"] + dvfiles, stderr=DEVNULL)
    DEVNULL.close()

    print
    print "Title:", talk["title"]
    print "Presenter:", talk["presenters"]
    print "Files:"
    dvfiles = [z["filepath"] + "/" + z["filename"] for z in talk["playlist"]]
    for i, dvfile in enumerate(dvfiles):
        print i, dvfile

    print
    # our users always type sensible things...right
    start_file = prompt_for_number("Start file", 0)
    start_offset = prompt_for_time("Start time offset", 0)
    end_file = prompt_for_number("End file", len(talk["playlist"])-1)
    end_offset = prompt_for_time("End time offset")

    print
    print "Starting job"
    # this basically prints the cut list which will be used later
    talk["cut_list"] = talk["playlist"][start_file:end_file+1]
    talk["cut_list"][0]["in"] = start_offset
    talk["cut_list"][-1]["out"] = end_offset

    create_mlt(talk, queue_todo_dir + "/" + str(talk['schedule_id']) + ".mlt")
    create_title(talk, queue_todo_dir + "/" + str(talk['schedule_id']) + ".png")

    print
    print "----------"
    print "Available jobs:", [t for t,v in jobs.items() if v["playlist"]]
    n = prompt_for_number("Select a job")
