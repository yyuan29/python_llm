from tools.utils import is_path_safe
import os


def cat(path):
    """
    Opens a file and returns its contents as a string.

    >>> # Basic file read
    >>> with open('test1.txt', 'w') as f:
    ...     _ = f.write('hello world')
    >>> cat('test1.txt')
    'hello world'

    >>> # File with multiple lines
    >>> with open('test2.txt', 'w') as f:
    ...     _ = f.write('line1\\nline2')
    >>> cat('test2.txt')
    'line1\\nline2'

    >>> # Empty file
    >>> with open('empty.txt', 'w') as f:
    ...     pass
    >>> cat('empty.txt')
    ''

    >>> # File does not exist
    >>> cat('does_not_exist.txt')
    "Error: File 'does_not_exist.txt' not found."

    >>> # Directory instead of file
    >>> os.mkdir('testdir')
    >>> cat('testdir')
    "Error: File 'testdir' not found."

    >>> # UTF-16 encoded file
    >>> with open('utf16.txt', 'w', encoding='utf-16') as f:
    ...     _ = f.write('hello utf16')
    >>> cat('utf16.txt')
    'hello utf16'

    >>> # Unsafe path
    >>> cat('/etc/passwd')
    'Error: unsafe path'

    >>> # Binary file (forces decode failure)
    >>> with open('binary.bin', 'wb') as f:
    ...     _ = f.write(b'\\x00\\xff\\x00\\xff')
    >>> cat('binary.bin')
    'Error: Could not decode file (likely binary).'
    """

    if not is_path_safe(path):
        return "Error: unsafe path"

    if not os.path.exists(path) or not os.path.isfile(path):
        return f"Error: File '{path}' not found."

    for encoding in ["utf-8", "utf-16"]:
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

    return "Error: Could not decode file (likely binary)."