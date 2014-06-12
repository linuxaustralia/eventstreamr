#!/usr/bin/python
# -*- coding: utf-8 -*-

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
from wand.drawing import Drawing
from wand.image import Image

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


'''
mi] = start_offset
       #talksi] = start_offset
       #talks[n]["files"][i]["out"] = end_offset
[n]["files"][i]["out"] = end_offset
lt = Element('mlt')

intro = SubElement(mlt, 'producer', id='intro')
    irint prettify(mlt)
intro_property = SubElement(intro, "property", name="resource")
intro_property.text = "intro.dv"
title = SubElement(mlt, "producer", id="title")
title_property = SubElement(title, 'property', name="resource")
title_property = "title.png"
play_intro = SubElement(mlt, "playlist", id="playlist0")
producer0 = SubElement(play_intro, "entry producer=\"intro\" in=\"0\" out=\"75\""   )
producer1 = SubElement(play_intro, "entry producer=\"title\" in=\"75\" out=\"1000000\"")
'''


'''
        
    intro = SubElement(mlt, 'producer', id='intro')
    intro_property = SubElement(intro, "property", name="resource")
    intro_property.text = "intro.dv"
    title = SubElement(mlt, "producer", id="title")
    title_property = SubElement(title, 'property', name="resource")
    title_property = "title.png"
    play_intro = SubElement(mlt, "playlist", id="playlist0")
    producer0 = SubElement(play_intro, "entry producer=\"intro\" in=\"0\" out=\"75\""   )
    producer1 = SubElement(play_intro, "entry producer=\"title\" in=\"75\" out=\"1000000\"")

    print prettify(mlt)

    tmpmlt.write(prettify(mlt));
    intro.close()
'''
'''

<?xml version="1.0" ?>
<mlt>
  <producer id="intro">
    <property name="resource">intro.dv</property>
  </producer>
  <producer id="title">
    <property name="resource"/>
  </producer>
  <playlist id="playlist0">
    <entry in="0" out="75" producer="intro"/>
    <entry in="75" out="1000000" producer="title"/>
  </playlist>
</mlt>

for i,dvfile in enumerate(dvfiles):
    irint prettify(mlt)
if start_file <= i <= end_file:
       extra = ""
       if i == start_file:
          extra = "(start: {0} seconds)".format(start_offset)
       if i == end_file:
          extra = "(end: {0} seconds)".format(end_offset)
       print dvfile, extra
       #talks[n]["files"][i]["in:", [t for t,v in talks.items() if v["playlist"]]
    n = prompt_for_number("Select a job")

       print talks[n]["files"][i]
    else:
        print talks[n]["files"].remove(i)
    print talks[n]["files"]
   <mlt>
 for file in cut_list:
        <producer id="filename">
          <property name="resource">filepath/filename</property>
        </producer>
        <playlist id="playlist0">
 for file in cut_list:
            <entry producer="filename" if file[in]: in="file[in]" if file[out] out="file[out]"/>
        </playlist>
        </mlt>
        
        # print mltfile
    # do lots of melt calculations or something here
    # then subprocess.Popen stuff

    print
    print "----------"
    print "Available jobs:", [t for t,v in talks.items() if v["files"]]
    n = prompt_for_number("Select a job")
'''
