#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib2
import sys
import os
import errno
import re

# magic foo to parse json file into config dict
# else load config from file below
config = {}

config['global_storage_path'] = "/home/av/recordings"
# If below is a local file please append 'file://' to the path
config['schedule_location'] = "http://2014.pycon-au.org/programme/schedule/json"
config['ftp_server_path'] = "ftp.example.com/pub"
config['ftp_user_name'] = 'test1234'
config['yt_username'] = 'mybillygoat'
config['yt_password'] = 'test1234'

def urlify(s):

     # Remove all non-word characters (everything except numbers and letters)
     s = re.sub(r"[^\w\s]", '', s)

     # Replace all runs of whitespace with a single dash
     s = re.sub(r"\s+", '_', s)

     return s

def mkdir_p(path):
    """ 'mkdir -p' in Python """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

programmedata_json = urllib2.urlopen(config['schedule_location'])
programmedata_final = json.load(programmedata_json)

room_number=0
rooms = {}
room_id = {}
rec_schedule = {}

#print room_number
#print len(programmedata_final['Breakout 1'])
#print (programmedata_final['Foyer'][0]['schedule_id'])

s = "many   fancy word \nhello    \thi"
print re.split('\s+', s)

# Make directories
for room in programmedata_final:
    for room_schedule in programmedata_final[room]:
        rec_schedule[room_schedule['schedule_id']] = {}
        rec_schedule[room_schedule['schedule_id']]['schedule_id'] = room_schedule['schedule_id']
        rec_schedule[room_schedule['schedule_id']]['start'] = room_schedule['start']
        rec_schedule[room_schedule['schedule_id']]['end'] = room_schedule['end']#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib2
import sys
import os
import errno
import re

# magic foo to parse json file into config dict
# else load config from file below
config = {}

config['global_storage_path'] = "/home/av/recordings"
# If below is a local file please append 'file://' to the path
config['schedule_location'] = "http://2014.pycon-au.org/programme/schedule/json"
config['ftp_server_path'] = "ftp.example.com/pub"
config['ftp_user_name'] = 'test1234'
config['yt_username'] = 'mybillygoat'
config['yt_password'] = 'test1234'

def urlify(s):

     # Remove all non-word characters (everything except numbers and letters)
     s = re.sub(r"[^\w\s]", '', s)

     # Replace all runs of whitespace with a single dash
     s = re.sub(r"\s+", '_', s)

     return s

def mkdir_p(path):
    """ 'mkdir -p' in Python """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

programmedata_json = urllib2.urlopen(config['schedule_location'])
programmedata_final = json
        rec_schedule[room_schedule['schedule_id']]['duration'] = room_schedule['duration']
        rec_schedule[room_schedule['schedule_id']]['room'] = room
        rec_schedule[room_schedule['schedule_id']]['title'] = room_schedule['title']
        #x = rec_schedule[room_schedule['schedule_id']]['path'] = storage_path + '/' + urlify(room) + rec_schedule[room_schedule['schedule_id']['start']
        #rec_schedule[room_schedule['schedule_id']]['path'] = storage_path + '/' + urlify(room) + re.split('\s+', rec_schedule[room_schedule['schedule_id']]['start'])
        rec_schedule[room_schedule['schedule_id']]['files'] = ['test1.dv', 'test2.dv']
        rec_schedule[room_schedule['schedule_id']]['distribution'] = ['yt', 'ftp']
        rec_schedule[room_schedule['schedule_id']]['yt_encoding_profile'] = 1
        rec_schedule[room_schedule['schedule_id']]['ftp_encoding_profile'] = 1 
        print str(rec_schedule[room_schedule['schedule_id']]['schedule_id']) + ": " + str(rec_schedule[room_schedule['schedule_id']]['room']) + " " + str(rec_schedule[room_schedule['schedule_id']]['start'])

selected_schedule = raw_input('Enter Schedule ID: ')
print selected_schedule
