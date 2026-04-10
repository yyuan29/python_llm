import os

def is_path_safe(path):
    if os.path.isabs(path):
        return False

    if ".." in path:
        return False

    return True