import os
import re
from tools.utils import is_path_safe


def grep(pattern, path):
    """
    Searches files for regex matches and returns matching lines.

    >>> grep("a", "../etc/passwd")
    'Error: unsafe path'

    >>> filename = "temp_test_file.txt"
    >>> _ = open(filename, "w").write("hello world\\nworld again\\n")
    >>> grep("hello", filename)
    'hello world'

    >>> grep("world", filename)
    'hello world\\nworld again'

    >>> os.remove(filename)

    >>> os.mkdir("tmp_dir")
    >>> _ = open("tmp_dir/file.txt", "w").write("hello world\\n")
    >>> _ = open("tmp_file.txt", "w").write("hello world\\n")

    >>> result = grep("hello", "tmp_dir")
    >>> "hello world" in result
    True

    >>> import shutil
    >>> os.remove("tmp_file.txt")
    >>> shutil.rmtree("tmp_dir")

    >>> filename = "tmp_bin.bin"
    >>> _ = open(filename, "wb").write(b"\\x00\\xff\\x00\\xff")
    >>> isinstance(grep("a", filename), str)
    True
    >>> os.remove(filename)

    >>> filename = "tmp_empty.txt"
    >>> _ = open(filename, "w").write("nothing here")
    >>> grep("zzz", filename)
    ''
    >>> os.remove(filename)
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
