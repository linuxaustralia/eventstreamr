from eventstreamr2.lib.file_helper import load_json

_undefined = object()


def load_config_file(conf_mgr, file, source, priority = _undefined):
    """
    Load a single configuration from a file and store it in the given conference manager.

    If ``priority`` is not given then it is loaded from the file(or defaults to ``None`` if it is missing). Otherwise it passes the value through to :meth:`set_config`.

    :param conf_mgr: Configuration manager.
    :type conf_mgr: eventstreamr2.configuration.ConfigurationManager
    :param str file: The file name.
    :param str source: The name of the configuration source to pass through to the manager.
    :param source: The priority of the configuration source to pass through to the manager.
    :type source: int or None
    """
    # If priority is None then load from file(key: _priority).
    # or leave to existing priority

    file_dict = load_json(file)

    if priority == _undefined:
        priority = file_dict.get("_priority", None)

    for service_name, config in file_dict.items():
        conf_mgr.set_config(service_name, source, priority, config)

def load_backup_config_file(conf_mgr, file):
    """
    Load a single configuration from a file and store it in the given conference manager.

    If ``priority`` is not given then it is loaded from the file(or defaults to ``None`` if it is missing). Otherwise it passes the value through to :meth:`set_config`.

    It expects a file of the format::

        {
            "source": {
                "_priority": 10
                "service": {
                    ...
                },
                "service2": {
                    ...
                }
            }
            "source2": {
                "_priority": 10
                ...
            }
        }

    :param conf_mgr: Configuration manager.
    :type conf_mgr: eventstreamr2.configuration.ConfigurationManager
    :param str file: The file name.
    :param str source: The name of the configuration source to pass through to the manager.
    :param source: The priority of the configuration source to pass through to the manager.
    :type source: int or None
    """

    file_dict = load_json(file)

    for source, source_dict in file_dict.items():
        if "_priority" in source_dict:
            conf_mgr.set_source_priority(source, source_dict.pop("_priority"))
        for service, service_cfg in source_dict.items():
            conf_mgr.set_config(service, source, service_cfg)
