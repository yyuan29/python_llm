from tools.utils import is_path_safe
import glob
import os


def ls(folder="."):
    """
    List files in a directory (non-recursive), space-separated.

    >>> isinstance(ls("."), str)
    True

    >>> "Error" in ls("../")  # unsafe path
    True

    >>> result = ls("")
    >>> isinstance(result, str)
    True

    >>> # Non-existent directory
    >>> "Error" in ls("does_not_exist")
    True

    >>> # Create test directory
    >>> os.mkdir("test_ls_dir")
    >>> with open("test_ls_dir/file1.txt", "w") as f:
    ...     _ = f.write("hi")
    >>> with open("test_ls_dir/file2.txt", "w") as f:
    ...     _ = f.write("hi")

    >>> out = ls("test_ls_dir")
    >>> "test_ls_dir/file1.txt" in out and "test_ls_dir/file2.txt" in out
    True
    """

    if not folder:
        folder = "."

    if not is_path_safe(folder):
        return "Error: unsafe path"

    if not os.path.exists(folder) or not os.path.isdir(folder):
        return f"Error: Directory '{folder}' not found."

    entries = sorted(glob.glob(os.path.join(folder, "*")))

    return " ".join(entries)