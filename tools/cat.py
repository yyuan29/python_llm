from tools.utils import is_path_safe


def cat(input):
    '''
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

        >>> # Binary / non-text file (simulate with bytes)
        >>> cat('tools/screenshot.png')
        'Error: Could not decode file (likely binary).'
        >>> # UTF-16 encoded file (Windows case)
        >>> with open('utf16.txt', 'w', encoding='utf-16') as f:
        ...     _ = f.write('hello utf16')
        >>> cat('utf16.txt')
        'hello utf16'

        >>> cat('/etc/passwd')
        'Error: unsafe path'

        >>> cat('testdir')
        "Error: File 'testdir' not found."

       '''
    if not is_path_safe(input):
        return "Error: unsafe path"
    for encoding in ['utf-8', 'utf-16']:
        try:
            with open(input, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            return f"Error: File '{input}' not found."
    return "Error: Could not decode file (likely binary)."
