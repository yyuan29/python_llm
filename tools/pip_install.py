import subprocess
import re


def pip_install(library_name: str) -> str:
    """
    Installs a Python library using pip3.

    Args:
        library_name (str): Name of the library to install.

    Returns:
        str: Success or error message.

    >>> isinstance(pip_install("requests"), str)
    True

    >>> "Error" in pip_install("")  # empty input should fail
    True

    >>> "Error" in pip_install("bad name!")  # invalid characters
    True
    """

    # Validate input
    if not library_name or not isinstance(library_name, str):
        return "Error: invalid library name"

    # Allow only typical PyPI-safe characters
    if not re.match(r"^[a-zA-Z0-9._-]+$", library_name):
        return "Error: library name contains invalid characters"

    try:
        result = subprocess.run(
            ["pip3", "install", library_name],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return f"Successfully installed {library_name}"
        else:
            return f"Error: {result.stderr.strip()}"

    except Exception as e:
        return f"Error: {str(e)}"