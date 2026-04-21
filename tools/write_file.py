from tools.write_files import write_files
from tools.doctests import doctests


def write_file(path, contents, commit_message):
    """
    Writes a single file and commits it.
    >>> import os
    >>> result = write_file("single_test.txt", "data", "add file")
    >>> os.path.isfile("single_test.txt")
    True
    >>> with open("single_test.txt") as f:
    ...     f.read()
    'data'
    >>> isinstance(result, str)
    True

    # cleanup
    >>> os.remove("single_test.txt")

    >>> from tools.write_file import write_file
    >>> import tools.doctests as dt

    >>> # mock doctests so we don't actually run subprocess
    >>> dt.doctests = lambda path: "fake doctest output"

    >>> result = write_file("test.py", "print('hi')", "commit")

    >>> "Doctest Results:" in result
    True

    >>> "fake doctest output" in result
    False
    """

    result = write_files(
        [{"path": path, "contents": contents}],
        commit_message
    )

    # run doctests if python file
    if path.endswith(".py"):
        test_output = doctests(path)
        return result + "\n\nDoctest Results:\n" + test_output

    return result
