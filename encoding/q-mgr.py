#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json
from pprint import pprint
import datetime
import time
import unicodedata
import string
import glob
import os
import codecs
from subprocess import call

# Main Constants
config_file = "file:///home/matt/eventstreamr/encoding/config.json"
recording_dir = 'recording/'
queue_dir = 'queue/'
completed_dir = 'completed/'

dates = []
rooms = []
schedule_ids = {}

json_format="%Y-%m-%d %H:%M:%S"
dv_format="%Y-%m-%d_%H-%M-%S"


def create_job(button):
    pass

def check_job(button):
    pass

def exit_program(button):
    raise urwid.ExitMainLoop()

def open_json(filename):
    json_data = urllib2.urlopen(filename)
    data = json.load(json_data)
    json_data.close()
    return data

# get the config_data which includes the base_dir and the schedule variables
config_data = open_json(config_file)
print config_data["schedule"]
#get the schedule config_data[base_dir] interate over the room/dates/ to find the times that are with the start time of the schedule
print config_data["base_dir"]
dvs = {}
files = []
rooms = []
dates = []

root_path = config_data["base_dir"] + recording_dir

for room in os.listdir(root_path):
	dates = {}
	for date in os.listdir(root_path + room):
		files = []
		for f in os.listdir(root_path + room + "/" + date):
			f = datetime.datetime.strptime(f[:-3], dv_format)
			files.append(f)
		dates[date] = files
	dvs[room] = dates
#print dvs
		
schedule_data = open_json(config_data["schedule"])
for k in schedule_data.keys():
	room = k.replace(" ", "")
	if room != k:
		schedule_data[room] = schedule_data[k]
        	del schedule_data[k]
	for z in schedule_data[room]:
		start_time = datetime.datetime.strptime(z['start'], json_format)
		buf_start_time = start_time - datetime.timedelta(minutes=10)
		#print start_time, buf_start_time
		end_time = datetime.datetime.strptime(z['end'], json_format)
		buf_end_time = end_time + datetime.timedelta(minutes=10)
		date = buf_start_time.strftime("%Y-%m-%d")
		try: 
			schedule = []
			for time in dvs[room][date]:
				if buf_start_time <= time <= buf_end_time:
					schedule.append(root_path + room + "/" + date + "/" +  time.strftime(dv_format) + ".dv")
			schedule_ids[z["schedule_id"]] = schedule
		except KeyError:
			print "file fail"


print "Available Jobs"
print schedule_ids
print "Select a job: "
selection = int(raw_input())
call(["vlc"] + schedule_ids[selection])

print "Select the files you bastard: "
i = 0
cut_list = {}
for x in schedule_ids[selection]:
	print "Do you want " + x + "? y/n"
	if raw_input() == "y":
		print "Do you want to trim the file? Please type in a value in secs say 10 from the start or -10 from the end "
		cut_list[x] = raw_input()

print cut_list


'''
for room, a in schedule_data.items():
        schedule_data[room]
        room.replace(" ", "")
        schedule_data[room]
        if schedule_data[room] not in rooms:
              rooms.append(room)
	for z in a:
		#print z['end']
		#print z['schedule_id']
		finish = z['end']
		date, time = finish.split()
		if date not in dates:
			dates.append(date)
schedule_ids.append(z['schedule_id']) 

print rooms
cnt schedule_data'''
