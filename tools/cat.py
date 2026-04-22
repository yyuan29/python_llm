from tools.utils import is_path_safe
import os


def cat(path):
    """
    Opens a file and reads it.
    >>> from tools.cat import cat
    >>> import os

    # basic read
    >>> with open("a.txt", "w") as f:
    ...     _ = f.write("hello")
    >>> cat("a.txt")
    'hello'

    # multiline
    >>> with open("b.txt", "w") as f:
    ...     _ = f.write("one\\ntwo")
    >>> cat("b.txt")
    'one\\ntwo'

    # empty file
    >>> open("c.txt", "w").close()
    >>> cat("c.txt")
    ''

    # file not found
    >>> cat("nope.txt")
    "Error: File 'nope.txt' not found."

    # directory instead of file
    >>> os.mkdir("mydir")
    >>> cat("mydir")
    "Error: File 'mydir' not found."

    # unsafe path
    >>> cat("/etc/passwd")
    'Error: unsafe path'

    # binary file
    >>> with open("bin.dat", "wb") as f:
    ...     _ = f.write(b"\\xff\\xfe\\xfd")
    >>> cat("bin.dat")
    'Error: Could not decode file (likely binary).'

    # cleanup
    >>> os.remove("a.txt")
    >>> os.remove("b.txt")
    >>> os.remove("c.txt")
    >>> os.remove("bin.dat")
    >>> os.rmdir("mydir")
    """

    # 1. safety check
    if not is_path_safe(path):
        return "Error: unsafe path"

    # 2. must exist and be a file
    if not os.path.exists(path) or not os.path.isfile(path):
        return f"Error: File '{path}' not found."

    # 3. try reading with common encodings
    for encoding in ["utf-8", "utf-16"]:
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

    # 4. binary or unreadable file
    return "Error: Could not decode file (likely binary)."
