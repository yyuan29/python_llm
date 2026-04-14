import os
import re
import glob
from tools.utils import is_path_safe


def grep(pattern, path):
    """
    Searches files for regex matches and returns matching lines.
    >>> grep("a", "../etc/passwd")
    'Error: unsafe path'

    >>> import os
    >>> filename = "temp_test_file.txt"
    >>> _ = open(filename, "w").write("hello world\\nworld again\\n")

    >>> grep("hello", filename)
    'hello world'

    >>> grep("world", filename)
    'hello world\\nworld again'

    >>> os.remove(filename)

    >>> import os
    >>> import shutil

    >>> os.mkdir("tmp_dir")
    >>> _ = open("tmp_dir/file.txt", "w").write("hello world\\n")

    >>> _ = open("tmp_file.txt", "w").write("hello world\\n")

    >>> result = grep("hello", "tmp_*")

    >>> "hello world" in result
    True

    >>> os.path.isdir("tmp_dir")
    True

    Cleanup

    >>> shutil.rmtree("tmp_dir")
    >>> os.remove("tmp_file.txt")

    >>> import os
    >>> filename = "tmp_strip.txt"
    >>> _ = open(filename, "w").write("hello world\\n   \\nworld again\\n")

    >>> grep("world", filename)
    'hello world\\nworld again'

    >>> os.remove(filename)

    >>> import os

    >>> filename = "tmp_bad.bin"
    >>> _ = open(filename, "wb").write(b"\\x00\\xff\\x00\\xff")

    >>> # Should not crash even though file is not valid UTF-8
    >>> isinstance(grep("a", filename), str)
    True

    >>> os.remove(filename)
    """
    if not is_path_safe(path):
        return "Error: unsafe path"
    results = []

    for fpath in sorted(glob.glob(path, recursive=True)):
        if os.path.isdir(fpath):
            continue

        try:
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.rstrip("\n")

                    if not line.strip():   # skip empty/space-only lines
                        continue

                    if re.search(pattern, line):
                        results.append(line)

        except (UnicodeDecodeError, OSError):
            continue

    return "\n".join(results)
