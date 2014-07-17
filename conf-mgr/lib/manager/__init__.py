__author__ = 'Lee Symes'

from lib import file_helper
import os

__queue_directories__ = {
    "todo": "todo/",
    "wip": "wip/",
    "done": "done/",
    "fail": "fail/"
}


def get_queue_directories(queue_base_dir, just_role_directory=None):
    base = os.path.normpath(queue_base_dir + "/")
    if just_role_directory in __queue_directories__:
        return os.path.join(queue_base_dir, __queue_directories__[just_role_directory])
    else:
        return {k: os.path.join(queue_base_dir, dir) for k,dir in __queue_directories__.iteritems()}