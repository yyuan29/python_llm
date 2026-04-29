import os


def is_path_safe(path):
    """
    Returns True if the path is safe (no absolute paths or traversal).
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
