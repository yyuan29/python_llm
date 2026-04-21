import os
import re
from tools.utils import is_path_safe


def grep(pattern, path):
    """
    Searches files for regex matches and returns matching lines.

    >>> from tools.grep import grep
    >>> import os

    >>> # unsafe path
    >>> grep("a", "../etc/passwd")
    'Error: unsafe path'


    >>> # basic single-line match
    >>> with open("t1.txt", "w") as f:
    ...     _ = f.write("hello world\\n")
    >>> grep("hello", "t1.txt")
    'hello world'

    >>> # multiple-line match
    >>> with open("t2.txt", "w") as f:
    ...     _ = f.write("hello world\\nworld again\\n")
    >>> grep("world", "t2.txt")
    'hello world\\nworld again'


    >>> # no match returns empty string
    >>> grep("zzz", "t2.txt")
    ''

    >>> # binary file still returns string (no crash)
    >>> with open("bin.bin", "wb") as f:
    ...     _ = f.write(b"\\x00\\xff\\x00")
    >>> isinstance(grep("a", "bin.bin"), str)
    True
    """

    # 1. safety check
    if not is_path_safe(path):
        return "Error: unsafe path"

    results = []

    # 2. build file list (handles both file and directory)
    files = []

    if os.path.isfile(path):
        files = [path]
    else:
        for root, _, fs in os.walk(path):
            for f in fs:
                files.append(os.path.join(root, f))

    # 3. search files
    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if re.search(pattern, line):
                        results.append(line.rstrip("\n"))
        except OSError:
            continue

    return "\n".join(results)
