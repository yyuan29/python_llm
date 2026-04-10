from tools.utils import is_path_safe
import glob


def ls(folder="."):
    """
    >>> # Testing the 'else' block (lines 23-25) by passing an empty string
    >>> 'README.md' in ls('')
    True
    >>> # Testing sorting logic for the current directory
    >>> result = ls('')
    >>> result == ' '.join(sorted(result.split()))
    True
    >>> # Testing error handling
    >>> ls('../')
    'Error: unsafe path'
    """
    if not is_path_safe(folder):
        return "Error: unsafe path"
    if folder:
        result = ''
        # folder + '/*' ==> tools/*
        # glob is nondeterminsiitc; no guarantees about order
        result = sorted(glob.glob(folder + '/*'))
        return ' '.join(result)
    else:
        result = ''
        result = sorted(glob.glob('*'))
        return ' '.join(result)
