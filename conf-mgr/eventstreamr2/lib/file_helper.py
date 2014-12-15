__author__ = 'Lee Symes'


def load_json(file_name):
    """
    Opens the file specified in read only mode, then reads as json; closes the file and then returns the json object.

    """
    with open(file_name, "r") as f:
        from json import load
        return load(f)


def save_json(object, file_name, compact=False, **kwargs):
    with open(file_name, "w") as f:
        # Sort by key name if it is not defined.
        kwargs.setdefault("sort_keys", True)
        if compact:
            # Make the json really compact.
            kwargs.setdefault('separators', (',', ':'))
        else:
            # By default don't use compact mode.
            # Add a respectable indent if an indent is not defined.
            kwargs.setdefault("indent", 4)
            # Remove trailing spaces from lines.
            kwargs.setdefault('separators', (',', ': '))
        from json import dump
        dump(object, f, **kwargs)


def object_to_json_string(object, compact=False, **kwargs):
    # Sort by key name if it is not defined.
    kwargs.setdefault("sort_keys", True)
    if compact:
        # Make the json really compact.
        kwargs.setdefault('separators', (',', ':'))
    else:
        # By default don't use compact mode.
        # Add a respectable indent if an indent is not defined.
        kwargs.setdefault("indent", 4)
        # Remove trailing spaces from lines.
        kwargs.setdefault('separators', (',', ': '))
    from json import dumps
    return dumps(object, **kwargs)


def read_in(file):
    with open(file, "r") as f:
        return f.read()


def isfile(file):
    import os
    return os.path.isfile(file)


def exists(file):
    import os
    return os.path.exists(file)


def delete(file):
    import os
    return os.remove(file)


def join(path, *paths):
    import os
    return os.path.join(path, *paths)



def list_files_in(folder, full_path=True):
    import os
    if os.path.isdir(folder):
        files = [os.path.join(folder, match) if full_path else match for match in os.listdir(folder)]
        return files
    else:
        return []


def list_filtered_files_in(folder, filename_pattern):
    import os
    if os.path.isdir(folder):
        import fnmatch
        all_files = os.listdir(folder)
        filtered_files = [os.path.join(folder, match) for match in fnmatch.filter(all_files, filename_pattern)]
        return filtered_files
    else:
        return []