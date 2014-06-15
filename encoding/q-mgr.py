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
schedule_file = os.path.join(base_dir, config_data['schedule'])
recording_dir = os.path.join(base_dir, 'recording')
queue_todo_dir = os.path.join(base_dir, 'queue', 'todo')
completed_dir = os.path.join(base_dir, 'completed')

json_format="%Y-%m-%d %H:%M:%S"

dv_format="%Y-%m-%d_%H-%M-%S"
dv_match_window = datetime.timedelta(minutes=10)
dv_frame_rate = 25

# Load the schedule
talks = get_schedule(schedule_file, json_format)
# Look for DV files that match the times from the schedule
for talk in talks:
    link_dv_files(talk, recording_dir, dv_match_window, dv_format)

# Create a dictionary of jobs and begin the main loop
jobs = { t['schedule_id']: t for t in talks if t['playlist'] }

print "Available jobs:", [t for t,v in jobs.items() if v['playlist']]
n = prompt_for_number("Select a job")

while n: 
    talk = jobs[n]

    dv_files = [os.path.join(dv_file['filepath'], dv_file['filename']) for dv_file in talk['playlist']]

    with open(os.devnull, 'wb') as DEVNULL:
        subprocess.Popen(['vlc'] + dv_files, stderr=DEVNULL)

    print
    print "Title:", talk['title']
    print "Presenter:", talk['presenters']
    print "Files:"
    for i, dv_file in enumerate(dv_files):
        print i, dv_file

    print
    # our users always type sensible things...right
    start_file = prompt_for_number("Start file", 0)
    start_offset = None
    while start_offset is None:
        start_offset = prompt_for_time("Start time offset", 0)
    end_file = prompt_for_number("End file", len(talk['playlist'])-1)
    end_offset = None
    while end_offset is None:
        end_offset = prompt_for_time("End time offset")

    # this sets up the cut_list which will be used later
    talk['cut_list'] = talk['playlist'][start_file:end_file+1]
    talk['cut_list'][0]['in'] = start_offset
    talk['cut_list'][-1]['out'] = end_offset

    print "Creating and queuing job " + str(talk['schedule_id'])
    job_file = os.path.join(queue_todo_dir, str(talk['schedule_id']))
    create_mlt(talk, job_file + '.mlt', dv_frame_rate)
    create_title(talk, job_file + '.title.png')

    print
    print "----------"
    print "Available jobs:", [t for t,v in jobs.items() if v['playlist']]
    n = prompt_for_number("Select a job")
