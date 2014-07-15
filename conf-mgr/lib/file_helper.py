__author__ = 'Lee Symes'


def load_json(file_name):
    """
    Opens the file specified in read only mode, then reads as json; closes the file and then returns the json object.

    """
    try:
        from json import load
        f = open(file_name, "r")
        obj = load(f)
    finally:
        f.close()
    return obj


def save_json(object, file_name, compact=False, **kwargs):
    try:
        f = open(file_name, "w")
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
    finally:
        f.close()


def list_files_in(folder, expand_subdirectories=False):
    import os
    if os.path.isdir(folder):
        files = os.listdir(folder)
        if expand_subdirectories:
            for sub_file in files:
                files.extend(list_files_in(sub_file,
                                           expand_subdirectories=expand_subdirectories))
        return files
    else:
        return []

def list_filtered_files_in(folder, filename_pattern, expand_subdirectories=False, subdirectory_name_pattern="*"):
    import os
    if os.path.isdir(folder):
        import fnmatch
        all_files = os.listdir(folder)
        filtered_files = fnmatch.filter(all_files, filename_pattern)
        if expand_subdirectories:
            for sub_file in all_files:
                if fnmatch.fnmatch(sub_file, subdirectory_name_pattern):
                    filtered_files.extend(list_filtered_files_in(sub_file, filename_pattern,
                                                                 expand_subdirectories=expand_subdirectories,
                                                                 subdirectory_name_pattern=subdirectory_name_pattern))
        return filtered_files
    else:
        return []