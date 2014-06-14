#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import os
import fnmatch
import time

from lib.schedule import open_json

config_file = 'config.json'
config_data = open_json(config_file)

node_name = 'test1'

base_dir = config_data['base_dir']
queue_todo_dir = os.path.join(base_dir, 'queue', 'todo')
queue_wip_dir = os.path.join(base_dir, 'queue', 'wip', node_name)
queue_done_dir = os.path.join(base_dir, 'queue', 'done')
completed_dir = os.path.join(base_dir, 'completed')
intro_file = os.path.join(base_dir, 'intro.dv')

def move_job(src_dir, dst_dir, jobname):
    files = os.listdir(src_dir)
    for filename in files:
        if fnmatch.fnmatch(filename, job + '.*'):
            src = os.path.join(src_dir, filename)
            dst = os.path.join(dst_dir, filename)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            os.rename(src, dst)

while True:
    files = os.listdir(queue_todo_dir)
    for filename in files:
        if fnmatch.fnmatch(filename, '*.mlt'): 
            job = filename[:-4]
            print "Starting job " + job
            move_job(queue_todo_dir, queue_wip_dir, job) 
            job_dv_file = os.path.join(completed_dir, job + '.dv')
            job_title_file = os.path.join(queue_wip_dir, job + '.title.png')
            pipeline = []
            pipeline.append(['melt', os.path.join(queue_wip_dir, filename), '-consumer', 'avformat:' + job_dv_file])
            pipeline.append(['melt', intro_file, '-filter', 'watermark:' + job_title_file, 'in=50', 'out=100', 'composite.progressive=1', 'oducer.align=centre', 'composite.valign=c', 'composite.halign=c', job_dv_file, '-consumer', 'avformat:' + os.path.join(completed_dir, job + '.ogv'), 'f=ogg', 'vcodec=libtheora', 'b=1000k', 'acodec=libvorbis', 'aq=25'])
            pipeline.append(['melt', intro_file, '-filter', 'watermark:' + job_title_file, 'in=50', 'out=100', 'composite.progressive=1', 'oducer.align=centre', 'composite.valign=c', 'composite.halign=c', job_dv_file, '-consumer', 'avformat:' + os.path.join(completed_dir, job + '.mp4'), 'f=mp4', 'vcodec=libx264'])
            log_file = os.path.join(queue_wip_dir, job + '.log')
            with open(log_file, 'w') as log:
                for args in pipeline:
                    process = subprocess.Popen(args, stdout=subprocess.PIPE)
                    (stdoutdata, stderrdata) = process.communicate()
                    if stdoutdata:
                        log.write(stdoutdata)
                    if stderrdata:
                        log.write(stderrdata)
            print "Finished job " + job
            move_job(queue_wip_dir, queue_done_dir, job)
    time.sleep(10)
