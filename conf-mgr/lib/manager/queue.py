__author__ = 'Lee Symes'

from lib import file_helper as files

class EncoderQueue:

    def __init__(self, folder, all_stations):
        self.all_stations = all_stations
        self.folder = folder

        # Initialise state variables

    def __call__(self):
        todo_files = files.list_filtered_files_in(self.folder)




