__author__ = 'Lee Symes'

import os
from lib import file_helper as files

class FilteredMonitor():

    def __init__(self, callback, run_filter=None):
        self.callback = callback
        if run_filter:
            self.run_filter = run_filter
        if not self.run_filter:
            raise Exception("There is no filter - or at least I don't think so.")

    def __call__(self, *args, **kwargs):
        if self.run_filter():
            self.callback(*args, **kwargs)


class FilesInFolderMonitor(FilteredMonitor):

    def __init__(self, folder, callback):
        self._folder = folder
        FilteredMonitor.__init__(self, callback)

    def run_filter(self):
        return files.list_files_in(self._folder)

class FilteredFilesInFolderMonitor(FilesInFolderMonitor):

    def __init__(self, folder, filename_pattern,  callback):
        self._filename_pattern = filename_pattern
        FilesInFolderMonitor.__init__(self, folder, callback)

    def run_filter(self):
        return files.list_filtered_files_in(self._folder, self._filename_pattern)

