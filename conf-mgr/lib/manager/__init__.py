__author__ = 'Lee Symes'

import os

__queue_directories__ = {
    "todo": "todo/",
    "wip": "wip/",
    "done": "done/",
    "fail": "fail/"
}


def get_queue_directories(queue_base_dir, just_role_directory=None):
    if just_role_directory in __queue_directories__:
        return os.path.join(queue_base_dir, __queue_directories__[just_role_directory])
    else:
        return {key: os.path.join(queue_base_dir, directory) for key, directory in __queue_directories__.iteritems()}
