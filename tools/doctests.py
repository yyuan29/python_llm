import subprocess
from tools.utils import is_path_safe


def doctests(path):
    """
    Runs doctests on a file.

    >>> from tools.doctests import doctests

    >>> # unsafe path check
    >>> doctests("/etc/passwd")
    'Error: unsafe path'


    >>> # returns a string for a valid file input (mocked behavior)
    >>> isinstance(doctests("fake.py"), str)
    True


    >>> # output always contains string result (stdout/stderr combined)
    >>> isinstance(doctests("any_file.py"), str)
    True

    >>> from tools.doctests import doctests
    >>> import subprocess

    >>> # force subprocess to raise an exception
    >>> subprocess.run = lambda *a, **k: (_ for _ in ()).throw(Exception("boom"))

    >>> doctests("fake.py")
    'Error: boom'
    """
    if not is_path_safe(path):
        return "Error: unsafe path"

    try:
        result = subprocess.run(
            ["python3", "-m", "doctest", "-v", path],
            capture_output=True,
            text=True
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {str(e)}"
