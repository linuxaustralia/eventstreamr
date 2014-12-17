import eventstreamr2.configuration as cfg

from eventstreamr2.lib.file_helper import load_json


def load_config_file(conf_mgr, file, source, priority = None):
    """

    """
    # If priority is None then load from file(key: _priority).
    # or leave to existing priority

    file_dict = load_json(file)

    if priority is None:
        priority = file_dict.get("_priority", None)

    for service_name, config in file_dict.items():
        conf_mgr.set_config(service_name, source, priority, config)
