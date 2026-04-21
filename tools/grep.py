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

    >>> import os
    >>> from tools.grep import grep

    >>> # create a small directory with a file inside
    >>> os.mkdir("d1")
    >>> with open("d1/a.txt", "w") as f:
    ...     _ = f.write("hello world\\n")

    >>> # grep should handle directory input by searching inside it
    >>> "hello world" in grep("hello", "d1")
    True

    >>> import shutil
    >>> shutil.rmtree("d1")

    >>> import os
    >>> from tools.grep import grep

    >>> # file that exists but is unreadable-safe check (still returns string, no crash)
    >>> with open("safe.txt", "w") as f:
    ...     _ = f.write("hello world\\n")

    >>> isinstance(grep("hello", "safe.txt"), str)
    True

    >>> import os
    >>> import builtins
    >>> from tools.grep import grep

    >>> # create a normal file
    >>> with open("ok.txt", "w") as f:
    ...     _ = f.write("hello world\\n")

    >>> # force open() to fail for this file (simulates OSError)
    >>> real_open = open
    >>> def fake_open(*args, **kwargs):
    ...     if "ok.txt" in args[0]:
    ...         raise OSError("blocked file")
    ...     return real_open(*args, **kwargs)

    >>> builtins.open = fake_open

    >>> # grep should not crash and should just skip file
    >>> isinstance(grep("hello", "ok.txt"), str)
    True

    >>> # restore open
    >>> builtins.open = real_open

    >>> os.remove("ok.txt")

    >>> os.remove("safe.txt")
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
