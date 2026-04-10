import os

def is_path_safe(path):
    # reject absolute paths
    if os.path.isabs(path):
        return False

    # reject directory traversal
    if ".." in path:
        return False

    return True