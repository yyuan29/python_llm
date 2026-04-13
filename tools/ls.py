from tools.utils import is_path_safe
import glob


def ls(folder="."):
    """
    Basic listing in current directory.

    >>> isinstance(ls("."), str)
    True

    >>> "Error" in ls("../")  # unsafe path check
    True

    >>> result = ls("")
    >>> isinstance(result, str)
    True
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
