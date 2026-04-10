import os


def is_path_safe(path):
    """
    Checks if a path is safe (not absolute and no directory traversal).

    >>> is_path_safe("documents/notes.txt")
    True
    >>> is_path_safe("/etc/passwd")
    False
    >>> is_path_safe("../secrets.py")
    False
    >>> is_path_safe("src/../config.json")
    False
    """
    if os.path.isabs(path):
        return False

    if ".." in path:
        return False

    return True
