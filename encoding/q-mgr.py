#!/usr/bin/python
# -*- coding: utf-8 -*-

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom

import urllib2
import json
import datetime
import os
import subprocess

from lib.schedule import *
from lib.ui import *

# Main Constants
config_file = "config.json"
recording_dir = 'recording'
queue_dir = 'queue'
completed_dir = 'completed'

schedule_ids = {}

json_format="%Y-%m-%d %H:%M:%S"
dv_format="%Y-%m-%d_%H-%M-%S"


# match items in the schedule with .dv files by timestamp
buffer = datetime.timedelta(minutes=10)

# read the config file
config_data = open_json(config_file)
base_dir = config_data["base_dir"]
schedule_file = base_dir + "/" + config_data["schedule"]
 
# first pass through the recording directory: find the times of all .dv files
recording_root = base_dir + "/" + recording_dir
talks = get_schedule(schedule_file, json_format)
for talk in talks:
    link_dv_files(talk, recording_root, buffer, dv_format)

"""
User interface stuff
"""



def get_duration(filename):
# from matt, untested since i don't have test files
# not quite sure what this returns/outputs
    cmd = "exiftool -duration " + filename
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout:
        print line.split()[2]
        return

#          'filename' : time.strftime(dv_format) + ".dv",
#          'filepath' : "/".join([recording_root, room, date])
DEVNULL = open(os.devnull, 'wb')

jobs = { t['schedule_id']: t for t in talks if t["playlist"] }

print "Available jobs:", [t for t,v in jobs.items() if v["playlist"]]
n = prompt_for_number("Select a job")

while n: 
    talk = jobs[n]
    
    dvfiles = [z["filepath"] + "/" + z["filename"] for z in talk["playlist"]]
    subprocess.Popen(["vlc"] + dvfiles, stderr=DEVNULL)

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
    start_offset = prompt_for_time("Start time offset (HH:MM:SS)", 0)
    end_file = prompt_for_number("End file", len(talk["playlist"])-1)
    end_offset = prompt_for_time("End time offset seconds (HH:MM:SS)", 0)
    # should probably be the end of the selected end_file using exiftool

    print
    print "Starting job"
    # this basically prints the cut list which will be used later
    talk["cut_list"] = talk["playlist"][start_file:end_file+1]
    print start_offset
    print end_offset
    talk["cut_list"][0]["in"] = int(start_offset.strftime("%s")) * 25
    talk["cut_list"][-1]["out"] = end_offset

#= start_offset
    talk["cut_list"][-1]["out"] = end_offset

    # Now onto the xml stuff. Very rough and ready but will clean up when it works. Need sleep will fix it up tomorrow/today ;-)
    tmpmlt = open(str(talk['schedule_id']) + ".mlt", 'w')
    mlt = Element('mlt')
    playlist = SubElement(mlt, "playlist", id="playlist0")
    for cut_file in talk["cut_list"]:
        producer = SubElement(mlt, 'producer', id=cut_file["filename"])
        producer_property = SubElement(producer, "property", name="resource")
        producer_property.text = cut_file["filepath"] + "/"  + cut_file["filename"]
        args = {} 
        args['producer'] = cut_file['filename']
        print duration(producer_property.text)
        if 'in' in cut_file:
            args['in'] = str(cut_file['in'])
        if 'out' in cut_file:
            args['out'] = str(cut_file['out'])
        playlist_entry = SubElement(playlist, "entry", args)


    image = Image(width=700, height=200)
    label = Drawing()
    label.font = '/usr/share/fonts/truetype/ubuntu-font-family/ubuntu-b.ttf'
    label.text_alignment = 'center'
    label.text(350, 100, talk['title']);
    label(image)
    image.format = 'png'
    image.save(filename=str(talk['schedule_id']) + ".png")


    ElementTree.ElementTree(mlt).write(str(talk['schedule_id']) + ".mlt")

    print
    print "----------"
    print "Available jobs:", [t for t,v in jobs.items() if v["playlist"]]
    n = prompt_for_number("Select a job")



