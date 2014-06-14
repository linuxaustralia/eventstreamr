import os
import urllib2
import json
import datetime

def dv_to_datetime(filename, filename_format):
    """ Return a datetime object if filename is <timestamp>.dv, else None """
    if filename[-3:] == ".dv":
        try:
            time = datetime.datetime.strptime(filename[:-3], filename_format)
        except ValueError:
            time = None
    else:
        time = None
    return time

def open_json(filename):
    if "://" in filename:
        json_data = urllib2.urlopen(filename)
    else:
        json_data = open(filename)
    data = json.load(json_data)
    json_data.close()
    return data

def get_schedule(schedule_file, json_format):
    # read the schedule file, removing spaces in room names
    raw = open_json(schedule_file)
    schedule_data = {k.replace(" ", ""):v for k,v in raw.items()}
    fields = ["schedule_id", "presenters", "title", "start", "end"]
    talks = []
    for schedule_room, schedule_room_data in schedule_data.iteritems():
        for schedule_talk in schedule_room_data:
            talk = {field: schedule_talk[field] for field in fields}
            talk['room'] = schedule_room
            talk['start'] = datetime.datetime.strptime(schedule_talk["start"], json_format)
            talk['end'] = datetime.datetime.strptime(schedule_talk["end"], json_format)
            talk['date'] = talk['start'].strftime("%Y-%m-%d")
            talks.append(talk)
    return talks

def link_dv_files(talk, recording_root, buffer, dv_format):
    talk['playlist'] = [] 
    talk_path = recording_root + "/" + talk['room'] + "/" + talk['date']
    if os.path.exists(talk_path):
        for filename in os.listdir(talk_path):
            time = dv_to_datetime(filename, dv_format) 
            if time and talk['start'] - buffer <= time <= talk['end'] + buffer:
                dv_file = {
                    'filename' : filename,
                    'filepath' : talk_path
                }
                talk['playlist'].append(dv_file)
