import os
import glob
import subprocess
from tools.utils import is_path_safe


def rm(path):
    """
    Deletes files matching a glob pattern and commits the change.

    >>> import os
    >>> import glob
    >>> import subprocess
    >>> from tools.rm import rm

    >>> # 1. unsafe path
    >>> rm("/etc/passwd")
    'Error: unsafe path'


    >>> # 2. no matches
    >>> rm("file_that_does_not_exist_123.txt")
    'No files matched'


    >>> # 3. safe file deletion (basic case)
    >>> with open("rm_test.txt", "w") as f:
    ...     _ = f.write("hello")

    >>> rm("rm_test.txt")
    'Git error: boom'


    >>> # file should be deleted
    >>> os.path.exists("rm_test.txt")
    False


    >>> # 4. glob returns unsafe path inside loop
    >>> glob.glob = lambda x: ["/etc/passwd"]
    >>> rm("anything")
    'Error: unsafe path'


    >>> # 5. file exists but is not a file (no removal)
    >>> glob.glob = lambda x: ["fake_dir"]
    >>> os.path.isfile = lambda x: False
    >>> rm("fake_dir")
    'No files removed'


    >>> # 6. git failure handling (forced exception)
    >>> glob.glob = lambda x: ["rm_test.txt"]
    >>> os.path.isfile = lambda x: True
    >>> subprocess.run = lambda *a, **k: (_ for _ in ()).throw(Exception("boom"))

    >>> with open("rm_test.txt", "w") as f:
    ...     _ = f.write("hello")

    >>> rm("rm_test.txt")
    'Git error: boom'

    >>> import os
    >>> import glob
    >>> import subprocess
    >>> from tools.rm import rm

    >>> # create file so removal actually happens
    >>> with open("rm_success.txt", "w") as f:
    ...     _ = f.write("hello")

    >>> # ensure glob finds it
    >>> glob.glob = lambda x: ["rm_success.txt"]

    >>> # ensure file check passes
    >>> os.path.isfile = lambda x: True

    >>> # mock git success (no exception)
    >>> subprocess.run = lambda *a, **k: None

    >>> rm("rm_success.txt")
    "Removed: ['rm_success.txt']"

    >>> os.path.exists("rm_success.txt")
    False
    """

    if not is_path_safe(path):
        return "Error: unsafe path"

    matches = glob.glob(path)

    if not matches:
        return "No files matched"

    removed = []

    for p in matches:
        if not is_path_safe(p):
            return "Error: unsafe path"

        if os.path.isfile(p):
            os.remove(p)
            removed.append(p)

    if not removed:
        return "No files removed"

    try:
        subprocess.run(["git", "add", "-u"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"[docchat] rm {path}"],
            check=True
        )
    except Exception as e:
        return f"Git error: {str(e)}"

    return f"Removed: {removed}"
