import eventstreamr2.configuration as cfg

from file_helper import load_json


def load_config_file(conf_mgr, file, source, priority=None):
    # If priority is None then load from file(key: priority).
    file_dict = load_json(file)

    if priority is None:
        # `.pop` to prevent them
        priority = file_dict.pop("priority")

    for service_name in file_dict:
        conf_mgr.set_config(service_name, source, file)
