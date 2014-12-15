__author__ = 'Lee Symes'

from eventstreamr2.lib.file_helper import join, exists, isfile, load_json, save_json


class StationConfigManager(object):

    def __init__(self, config_folder):
        self.config_folder = config_folder

    @property
    def config_folder(self):
        return self.__config_folder

    @config_folder.setter
    def config_folder(self, folder):
        import os
        path = os.path.abspath(folder)
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.isdir(path):
            raise ValueError("Needs to be a directory")
        self.__config_folder = path

    def get_config_for(self, mac_address):
        file = self.get_file_for(mac_address)
        if file is not None:
            return load_json(file)
        else:
            return None

    def set_config_for(self, mac_address, config):
        print "MAC ADDRESS: %s" % mac_address
        file = self.get_file_for(mac_address, missing_ok=True)
        print "%s -> %r" % (file, config)
        if file is not None:
            save_json(config, file)
            return True
        else:
            return None

    def merge_config(self, config_1, config_2):
        """
        In the event of a timestamp conflict, config_1 is given priority. Otherwise it is existence followed by
        timestamp priority merge.

        :param config_1:
        :type config_1: dict(string, dict(string, dict(string, object))
        :param config_2:
        :type config_2: dict(string, dict(string, dict(string, object)))
        :return:
        :rtype:
        """
        if not config_2:
            return config_1
        if not config_1:
            return config_2
        output = {}
        roles = set(config_1.iterkeys()).union(set(config_2.iterkeys()))
        for role in roles:
            c1 = config_1.get(role, {})
            c2 = config_2.get(role, {})
            uuids = set(c1.iterkeys()).union(set(c2.iterkeys()))
            if uuids:
                output[role] = {}
                for uuid in uuids:
                    if uuid in c1 and uuid in c2:
                        # Timestamp check & combine
                        c1t = c1[uuid].get("timestamp", 0)
                        c2t = c2[uuid].get("timestamp", 0)
                        if c1t >= c2t:
                            output[role][uuid] = c1[uuid]
                        else:  # if c1t < c2t
                            output[role][uuid] = c2[uuid]
                    elif uuid in c1:
                        output[role][uuid] = c1[uuid]
                    elif uuid in c2:
                        output[role][uuid] = c1[uuid]
        return output

    def update_timestamps(self, config):
        """

        :param config:
        :type config: dict(string, dict(string, dict(string, object)))
        :return:
        :rtype:
        """
        #TODO Move this out to be a static method(maybe in eventstreamr2.lib.config instead)
        import time
        ts = long(time.time() * 1000)
        for r in config.itervalues():
            for u in r.itervalues():
                u["timestamp"] = ts

    def get_file_for(self, mac_address, missing_ok=False):
        clean_mac = str(mac_address).translate(None, "|:/\\")

        file = join(self.config_folder, clean_mac + ".json")
        if isfile(file) or (missing_ok and not exists(file)):
            return file
        else:
            return None
