from tools.utils import is_path_safe
import os


def cat(path):
    """
    Opens a file and returns its contents as a string.

    >>> with open('test1.txt', 'w') as f:
    ...     _ = f.write('hello world')
    >>> cat('test1.txt')
    'hello world'

    >>> with open('test2.txt', 'w') as f:
    ...     _ = f.write('line1\\nline2')
    >>> cat('test2.txt')
    'line1\\nline2'

    >>> with open('empty.txt', 'w') as f:
    ...     pass
    >>> cat('empty.txt')
    ''

    >>> cat('does_not_exist.txt')
    "Error: File 'does_not_exist.txt' not found."

    >>> os.mkdir('testdir')
    >>> cat('testdir')
    "Error: File 'testdir' not found."

    >>> cat('/etc/passwd')
    'Error: unsafe path'
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
