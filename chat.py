import os
import readline
from groq import Groq
from dotenv import load_dotenv

from tools.ls import ls
from tools.cat import cat
from tools.grep import grep
from tools.calculate import calculate
from tools.compact import compact
from tools.doctests import doctests
from tools.write_file import write_file
from tools.write_files import write_files
from tools.rm import rm

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
_SYSTEM_PROMPT = """
You are a file system automation agent.

YOU MUST FOLLOW THESE RULES EXACTLY:

1. If the user asks to create, edit, or write a file:
   Respond ONLY with:

/write_file <path> <contents> <commit_message>

2. Do NOT explain anything.
3. Do NOT respond in normal sentences.
4. Do NOT use markdown.
5. If you do not follow these rules, your response is invalid.

Example:
User: create greet.py with hello function
Assistant:
/write_file greet.py "def greet(): print('hello')" "add greet function"
"""
# =========================
# CHAT CLASS
# =========================


class Chat:
    """
    LLM chat wrapper.
    """

    def __init__(self, mock=False):
        """
        >>> chat = Chat(mock=True)
        >>> isinstance(chat.messages, list)
        True
        >>> chat.messages[0]["role"]
        'system'
        >>> "Respond clearly" in chat.messages[0]["content"]
        False
        >>> chat.mock
        True
        """
        self.client = Groq()
        self.mock = mock
        self.messages = [
            {"role": "system", "content": _SYSTEM_PROMPT}
        ]

    def send_message(self, message, temperature=0.0):
        """
        Sends a response based on what was given.
        >>> chat = Chat()

        >>> class FakeMessage:
        ...     def __init__(self, content):
        ...         self.content = content

        >>> class FakeChoice:
        ...     def __init__(self, content):
        ...         self.message = FakeMessage(content)

        >>> class FakeResponse:
        ...     def __init__(self, content):
        ...         self.choices = [FakeChoice(content)]

        >>> def fake_create(**kwargs):
        ...     return FakeResponse("ok")

        >>> chat.client.chat.completions.create = fake_create

        >>> chat.send_message("hello")
        'ok'

        >>> chat.messages[-1]["content"]
        'ok'
        """
        self.messages.append({"role": "user", "content": message})

        # call model safely
        try:
            resp = self.client.chat.completions.create(
                messages=self.messages,
                model="llama-3.1-8b-instant",
                temperature=temperature,
            )
        except Exception as e:
            return f"API error: {e}"

        msg = resp.choices[0].message

        # handle empty / None content
        out = msg.content or ""
        if not out:
            return "Error: empty model response"

        # store assistant response
        self.messages.append({"role": "assistant", "content": out})

        # =========================
        # TOOL HANDLING
        # =========================
        if out.startswith("/"):
            parts = out[1:].strip().split(" ", 2)

            cmd = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            if cmd == "write_file":
                if len(args) == 2:
                    args.append("update file")
                elif len(args) == 1:
                    args.append("")
                    args.append("update file")
            tools = {
                "ls": ls,
                "cat": cat,
                "grep": grep,
                "calculate": calculate,
                "compact": lambda *args: compact(self),
                "doctests": doctests,
                "write_file": write_file,
                "write_files": write_files,
                "rm": rm,
                "delete_file": rm,
            }

            tool = tools.get(cmd)

            try:
                if tool is None:
                    result = f"Error: unknown tool {cmd}"
                else:
                    result = tool(*args)
            except Exception as e:
                result = f"Tool error: {e}"

            # log tool result back into conversation
            self.messages.append({
                "role": "system",
                "content": f"{cmd} output: {result}"
            })

            return result

        # normal response
        return out


# =========================
# COMPLETER
# =========================
COMMANDS = [
    "ls", "cat", "grep", "calculate", "compact",
    "doctests", "write_file", "write_files", "rm"
]


def completer(text, state):
    """
    Tab completion.

    >>> callable(completer)
    True

    >>> import unittest.mock

    # Slash command completion
    >>> with unittest.mock.patch('readline.get_line_buffer') as mock_gb:
    ...     mock_gb.return_value = '/c'
    ...     [completer('c', i) for i in range(5)]
    ['cat', 'calculate', 'compact', None, None]

    # No buffer
    >>> with unittest.mock.patch('readline.get_line_buffer') as mock_gb:
    ...     mock_gb.return_value = ''
    ...     completer('', 0) is None
    True

    >>> import os, tempfile, unittest.mock

    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     p1 = os.path.join(tmp, "file1.txt")
    ...     p2 = os.path.join(tmp, "file2.txt")
    ...     open(p1, "w").close()
    ...     open(p2, "w").close()
    ...
    ...     with unittest.mock.patch('readline.get_line_buffer') as m:
    ...         m.return_value = 'file'
    ...         base = os.path.join(tmp, "file")
    ...         results = [completer(base, i) for i in range(3)]
    ...
    ...     any("file1.txt" in r for r in results if r)
    True
    """
    buffer = readline.get_line_buffer()
    if not buffer:
        return None

    parts = buffer.split()

    if buffer.startswith("/") and len(parts) <= 1:
        prefix = text.lstrip("/")
        matches = [c for c in COMMANDS if c.startswith(prefix)]
        return matches[state] if state < len(matches) else None

    dirname = os.path.dirname(text) or "."
    basename = os.path.basename(text)

    try:
        entries = os.listdir(dirname)
    except OSError:
        return None

    matches = []
    for e in entries:
        full = os.path.join(dirname, e)
        if e.startswith(basename):
            matches.append(full + ("/" if os.path.isdir(full) else ""))

    return matches[state] if state < len(matches) else None


# =========================
# REPL
# =========================
def repl():
    """
    A Read-Eval-Print Loop for the chat agent.
    >>> import os

    >>> # simulate missing .git folder
    >>> if os.path.isdir(".git"):
    ...     _ = os.rename(".git", ".git_backup")

    >>> repl()  # should print error and exit
    Error: .git folder not found

    >>> if os.path.isdir(".git_backup"):
    ...     _ = os.rename(".git_backup", ".git")

    >>> import os
    >>> import os, tempfile

    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     cwd = os.getcwd()
    ...     os.chdir(tmp)
    ...     os.mkdir(".git")
    ...     with open("AGENTS.md", "w") as f:
    ...         _ = f.write("agent rules")
    ...
    ...     import builtins
    ...     inputs = iter(["/exit"])
    ...     builtins.input = lambda _: next(inputs)
    ...
    ...     repl()  # should run without error
    ...
    ...     os.chdir(cwd)
    >>> if os.path.exists("AGENTS.md"): os.remove("AGENTS.md")

    >>> import builtins

    # Simulate EOFError when input() is called
    >>> def fake_input(prompt):
    ...     raise EOFError

    >>> builtins.input = fake_input

    >>> repl()

    >>> import builtins
    >>> inputs = iter(["/", "/exit"])
    >>> builtins.input = lambda _: next(inputs)
    >>> repl()  # doctest: +ELLIPSIS
    Error: unknown command

    >>> import builtins
    >>> inputs = iter(["/abc", "/exit"])
    >>> builtins.input = lambda _: next(inputs)
    >>> repl()  # doctest: +ELLIPSIS
    Error: unknown command abc

    >>> import builtins
    >>> inputs = iter(["/rm fakefile", "/exit"])
    >>> builtins.input = lambda _: next(inputs)
    >>> repl()  # doctest: +ELLIPSIS
    No files matched

    >>> import builtins
    >>> inputs = iter(["/ls .github", "/exit"])
    >>> builtins.input = lambda _: next(inputs)
    >>> repl()  # doctest: +ELLIPSIS
    .github/workflows

    >>> import builtins
    >>> def fake_input(_):
    ...     raise KeyboardInterrupt
    >>> builtins.input = fake_input
    >>> repl()
    <BLANKLINE>
    """
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    chat = Chat(mock=True)

    if not os.path.isdir(".git"):
        print("Error: .git folder not found")
        return

    if os.path.isfile("AGENTS.md"):
        content = cat("AGENTS.md")
        chat.messages.append({
            "role": "system",
            "content": f"Loaded AGENTS.md:\n{content}"
        })

    command_map = {
        "ls": ls,
        "cat": cat,
        "grep": grep,
        "calculate": calculate,
        "compact": lambda *args: compact(chat),
        "doctests": doctests,
        "write_file": write_file,
        "write_files": write_files,
        "rm": rm,
        "delete_file": rm,
    }

    try:
        while True:
            try:
                user_input = input("chat> ")
            except EOFError:
                break

            if not user_input:
                continue

            user_input = user_input.strip()

            if user_input.lower() in ("/exit", "/quit"):
                break

            if user_input.startswith("/"):
                parts = user_input[1:].split()
                if not parts:
                    print("Error: unknown command")
                    continue

                cmd, *args = parts
                if cmd not in command_map:
                    print(f"Error: unknown command {cmd}")
                    continue

                try:
                    result = command_map[cmd](*args)
                except Exception as e:
                    result = f"Error: {str(e)}"

                print(result)
                chat.messages.append({"role": "system",
                                      "content": f"{cmd} output:{result}"})
                continue

            print(chat.send_message(user_input))

    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    repl()
