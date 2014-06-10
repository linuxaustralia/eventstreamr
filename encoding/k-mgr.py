#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json
import datetime
import os
import subprocess

# Main Constants
config_file = "config.json"
recording_dir = 'recording'
queue_dir = 'queue'
completed_dir = 'completed'

schedule_ids = {}

json_format="%Y-%m-%d %H:%M:%S"
dv_format="%Y-%m-%d_%H-%M-%S"


def open_json(filename):
    if "://" in filename:
	json_data = urllib2.urlopen(filename)
    else:
	json_data = open(filename)
    data = json.load(json_data)
    json_data.close()
    return data

def dv_to_datetime(filename):
    """ Return a datetime object if filename is <timestamp>.dv, else None """
    if filename[-3:] == ".dv":
	try:
	    time = datetime.datetime.strptime(filename[:-3], dv_format)
	except ValueError:
	    time = None
    else:
	time = None
    return time

def potential_files(dv_list, start, end, buffer):
    """ Return a list of times that are roughly within start & end times """
    files = []
    for time in dv_list:
	if start-buffer <= time <= end+buffer:
	    filename = time.strftime(dv_format) + ".dv"
	    full = "/".join([recording_root, room, date, filename])
	    files.append(full)
    return sorted(files)


# read the config file
config_data = open_json(config_file)
base_dir = config_data["base_dir"]
schedule_file = base_dir + "/" + config_data["schedule"]

# first pass through the recording directory: find the times of all .dv files
recording_root = base_dir + "/" + recording_dir
dvs = {}
for room in os.listdir(recording_root):
    dates = {}
    room_path = recording_root + "/" + room
    for date in os.listdir(room_path):
	date_path = room_path + "/" + date
	dates[date] = [dv_to_datetime(f) for f in os.listdir(date_path)]
    dvs[room] = dates

# read the schedule file, removing spaces in room names
raw = open_json(schedule_file)
schedule_data = {k.replace(" ", ""):v for k,v in raw.items()}

# match items in the schedule with .dv files by timestamp
buffer = datetime.timedelta(minutes=1)
fields = ["presenters", "title", "start", "end"]
talks = {}
for room in schedule_data:
    for talk in schedule_data[room]:
	id = talk["schedule_id"]
	talks[id] = {k:talk[k] for k in fields}
	start = datetime.datetime.strptime(talk["start"], json_format)
	end = datetime.datetime.strptime(talk["end"], json_format)
	date = start.strftime("%Y-%m-%d")
	try: 
	    files = potential_files(dvs[room][date], start, end, buffer)
	except KeyError:
	    files = []
	talks[id]["files"] = files

"""
User interface stuff
"""

"""
print "Available Jobs"
print schedule_ids
print "Select a job: "
selection = int(raw_input())
call(["vlc"] + schedule_ids[selection])

print "Select the files you bastard: "
i = 0
cut_list = {}
for x in talks[selection]:
	print "Do you want " + x + "? y/n"
	if raw_input() == "y":
		print "Do you want to trim the file? y/n"
		if raw_input() == "y":
			print "Please type in a value in secs say 10 from the start or -10 from the end "
			cut_list[x] = int(raw_input())
		else:
			cut_list[x] = 0
	talks[x] = {}
print talks

"""

def prompt(string, default=None):
    """ Return user input, or default value if they just press enter """
    if default is not None:
	return raw_input("{0} [{1}]: ".format(string, default)) or default
    else:
	return raw_input("{0}: ".format(string))

def prompt_for_number(string, default=None):
    """ Return user input as an int if possible, else None """
    response = prompt(string, default)
    try:
	return int(response)
    except ValueError:
	return None

def get_duration(filename):
    # from matt, untested since i don't have test files
    # not quite sure what this returns/outputs
    cmd = "exiftool -duration " + filename
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout:
	print line.split()[2]
    return

DEVNULL = open(os.devnull, 'wb')
print "Available jobs:", [t for t,v in talks.items() if v["files"]]
n = prompt_for_number("Select a job")
while n:
    try:
	subprocess.Popen(["vlc"] + talks[n]["files"], stderr=DEVNULL)
    except KeyError:
	n = prompt_for_number("Select a job")
	continue

    print
    print "Title:", talks[n]["title"]
    print "Presenter:", talks[n]["presenters"]
    print "Files:"
    for i,f in enumerate(talks[n]["files"]):
	print i, f.split("/")[-1]

    print
    # our users always type sensible things...right
    start_file = prompt_for_number("Start file", 0)
    start_offset = prompt_for_number("Start time offset seconds", 0)
    end_file = prompt_for_number("End file", len(talks[n]["files"])-1)
    end_offset = prompt_for_number("End time offset seconds", 0)
    # should probably be the end of the selected end_file using exiftool

    print
    print "Starting job {0}".format(n)
    # this basically prints the cut list which will be used later
    for i,f in enumerate(talks[n]["files"]):
	if i < start_file or i > end_file:
	    continue
	extra = ""
	if i == start_file:
	    extra = "(start: {0} seconds)".format(start_offset)
	if i == end_file:
	    extra = "(end: {0} seconds)".format(end_offset)
	print f.split("/")[-1], extra

    # do lots of melt calculations or something here
    # then subprocess.Popen stuff

    print
    print "----------"
    print "Available jobs:", [t for t,v in talks.items() if v["files"]]
    n = prompt_for_number("Select a job")
