__author__ = 'Lee Symes'

from lib import file_helper

__queue_directories__ = {
    "todo": "todo/",
    "wip": "wip/",
    "done": "done/",
    "fail": "fail/"
}


def get_queue_directories(queue_base_dir, just_role_directory=None):
    base = file_helper.standardise_directory(queue_base_dir)
    if just_role_directory in __queue_directories__:
        return file_helper.standardise_directory(queue_base_dir + __queue_directories__[just_role_directory])
    else:
        return {k: file_helper.standardise_directory(queue_base_dir + v) for k,v in __queue_directories__.iteritems()}