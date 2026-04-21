from tools.utils import is_path_safe
import os


def cat(path):
    """
    Opens a file and returns its contents as a string.

    >>> import os
    >>> from tools.cat import cat

    >>> # basic file read
    >>> with open("test1.txt", "w") as f:
    ...     _ = f.write("hello world")
    >>> cat("test1.txt")
    'hello world'


    >>> # multiline file read
    >>> with open("test2.txt", "w") as f:
    ...     _ = f.write("line1\\nline2")
    >>> cat("test2.txt")
    'line1\\nline2'


    >>> # empty file
    >>> open("empty.txt", "w").close()
    >>> cat("empty.txt")
    ''


    >>> # file does not exist
    >>> cat("does_not_exist.txt")
    "Error: File 'does_not_exist.txt' not found."


    >>> # directory instead of file
    >>> os.mkdir("testdir")
    >>> cat("testdir")
    "Error: File 'testdir' not found."


    >>> # unsafe path
    >>> cat("/etc/passwd")
    'Error: unsafe path'

    >>> import os
    >>> from tools.cat import cat

    >>> # normal utf-8 file (no decode error path triggered)
    >>> with open("utf8.txt", "w", encoding="utf-8") as f:
    ...     _ = f.write("hello")
    >>> cat("utf8.txt")
    'hello'

    >>> import os
    >>> from tools.cat import cat

    >>> # create a truly invalid UTF file (forces fallback reliably)
    >>> with open("binary.txt", "wb") as f:
    ...     _ = f.write(b"\\x80\\x81\\x82\\x83")

    >>> cat("binary.txt") == "Error: Could not decode file (likely binary)."
    True

    >>> import os
    >>> from tools.cat import cat

    >>> # -----------------------------------
    >>> # basic binary file (covers fallback path indirectly)
    >>> # -----------------------------------
    >>> with open("binary.txt", "wb") as f:
    ...     _ = f.write(b"\\x00\\xff\\x00\\xff")

    >>> result = cat("binary.txt")
    >>> isinstance(result, str)
    True
    >>> "Could not decode" in result or result.startswith("Error")
    True

    >>> os.remove("binary.txt")


    >>> # -----------------------------------
    >>> # normal file ensures encoding loop works
    >>> # (implicitly skips UnicodeDecodeError branch safely)
    >>> # -----------------------------------
    >>> with open("utf8.txt", "w", encoding="utf-8") as f:
    ...     _ = f.write("hello")

    >>> cat("utf8.txt")
    'hello'

    >>> os.remove("utf8.txt")
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
