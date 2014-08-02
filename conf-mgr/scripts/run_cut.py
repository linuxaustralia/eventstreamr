#!/usr/bin/python

__author__ = 'lee'

from sys import argv, stderr, stdout
from json import loads
import os
from os.path import join

def header(title):
    print "#" * 120
    print "#" + (" " * 118) + "#"
    print "#" + title.center(118) + "#"
    print "#" + (" " * 118) + "#"
    print "#" * 120

def call(*args, **kwargs):
    from subprocess import call
    kwargs.update(stdout=stdout, stderr=stderr, cwd=job_folder)
    r = call(*args, **kwargs)
    if r != 0:
        exit(r)


json = loads(argv[-1])

job_folder = os.path.abspath(json["base-folder"])

in_time = json["in_time"]
out_time = json["out_time"]
out_file = join(job_folder, json["main"]["filename"])
file_list = json["file_list"]
schedule_id = json["schedule_id"]

args = ["xvfb-run", "-a", "melt", "-silent", file_list[0], "in=" + in_time]
args += file_list[1:]
args += ["out=" + out_time, "-consumer", "avformat:" + out_file]


call(args)

