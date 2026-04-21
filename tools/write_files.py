import os
import subprocess
from tools.utils import is_path_safe


def write_files(files, commit_message):
    """
    Writes multiple files and commits them.

    >>> import os
    >>> import subprocess
    >>> from tools.write_files import write_files

    >>> # -----------------------------
    >>> # 1. successful write + git add/commit path (LINE 40 + 58-59)
    >>> # -----------------------------
    >>> files = [
    ...     {"path": "wf1.txt", "contents": "hello"},
    ...     {"path": "wf2.txt", "contents": "world"}
    ... ]

    >>> # mock git success so subprocess.run doesn't throw
    >>> subprocess.run = lambda *a, **k: None

    >>> result = write_files(files, "my commit")

    >>> os.path.exists("wf1.txt")
    True
    >>> os.path.exists("wf2.txt")
    True

    >>> "Committed files" in result
    True


    >>> # cleanup
    >>> os.remove("wf1.txt")
    >>> os.remove("wf2.txt")


    >>> # -----------------------------
    >>> # 2. git failure path (ensures exception handling works)
    >>> # covers subprocess.run commit failure branch
    >>> # -----------------------------
    >>> files = [{"path": "wf3.txt", "contents": "x"}]

    >>> subprocess.run = lambda *a, **k: (_ for _ in ()).throw(Exception("boom"))

    >>> write_files(files, "fail commit")
    'Git error: boom'

    >>> os.path.exists("wf3.txt")
    True

    >>> from tools.write_files import write_files

    >>> # force unsafe path
    >>> import tools.write_files as wf
    >>> wf.is_path_safe = lambda path: False

    >>> files = [{"path": "bad.txt", "contents": "x"}]

    >>> write_files(files, "commit")
    'Error: unsafe path'
    """
    written_files = []

    for file in files:
        path = file["path"]
        contents = file["contents"]

        if not is_path_safe(path):
            return "Error: unsafe path"

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(contents)

        written_files.append(path)

    try:
        # git add
        subprocess.run(["git", "add"] + written_files, check=True)

        # git commit
        subprocess.run(
            ["git", "commit", "-m", f"[docchat] {commit_message}"],
            check=True
        )
    except Exception as e:
        return f"Git error: {str(e)}"

    return f"Committed files: {written_files}"
    # git add + commit
    repo.index.add(written_files)
    repo.index.commit(f"[docchat] {commit_message}")

    return f"Committed files: {written_files}"

