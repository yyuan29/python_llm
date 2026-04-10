import os
import re
import glob
from tools.utils import is_path_safe


def grep(pattern, path):
    """
    Setup for testing:
    >>> with open('test_a.txt', 'w') as f:
    ...     _ = f.write('hello world\\nbye world')
    >>> with open('test_b.txt', 'w') as f:
    ...     _ = f.write('solar system')

    Basic Match:
    >>> grep('hello', 'test_a.txt')
    'hello world'

    Multiple Line Match:
    >>> grep('world$', 'test_a.txt')
    'hello world\\nbye world'

    No Match:
    >>> grep('zzz', 'test_a.txt')
    ''

    Glob Pattern Match:
    >>> grep('world|system', 'test_*.txt')
    'hello world\\nbye world\\nsolar system'


    >>> grep("hello", "/etc/passwd")
    'Error: unsafe path'

    Cleanup:
    >>> import os
    >>> for f in glob.glob('test_*.txt'): os.remove(f)

    >>> grep('hello','tools/screenshot.png')
    ''

    >>> import os
    >>> with open('t_bin', 'wb') as f: _ = f.write(b'\\xff')
    >>> with open('t_txt', 'w') as f: _ = f.write('valid_match')
    >>> grep('valid', 't*')
    'valid_match'
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
                    if re.search(pattern, line):
                        results.append(line.strip())

        except (UnicodeDecodeError, OSError):
            continue

    return "\n".join(results)
