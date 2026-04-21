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

load_dotenv()

_SYSTEM_PROMPT = "Respond clearly in 1-2 sentences."

# =========================
# CHAT CLASS
# =========================
class Chat:
    """
    LLM chat wrapper.
    """

    def __init__(self, mock=False):
        self.client = Groq()
        self.mock = mock
        self.messages = [
            {"role": "system", "content": _SYSTEM_PROMPT}
        ]

    def send_message(self, message, temperature=0.0):
        """
        Sends a message to the LLM and returns the assistant's response.

        >>> chat = Chat()
        >>> class FakeMessage:
        ...     def __init__(self):
        ...         self.content = "ok"
        >>> class FakeChoice:
        ...     def __init__(self):
        ...         self.message = FakeMessage()
        >>> class FakeResponse:
        ...     choices = [FakeChoice()]
        >>> captured = {}
        >>> def fake_create(**kwargs):
        ...     captured["messages"] = kwargs["messages"]
        ...     return FakeResponse()
        >>> chat.client.chat.completions.create = fake_create

        >>> chat.send_message("hello")
        'ok'

        >>> chat.messages[-2]["content"]
        'hello'

        >>> captured["messages"][-1]["content"]
        'ok'
        """
        self.messages.append({"role": "user", "content": message})

        resp = self.client.chat.completions.create(
            messages=self.messages,
            model="llama-3.1-8b-instant",
            temperature=temperature,
        )

        out = resp.choices[0].message.content
        self.messages.append({"role": "assistant", "content": out})
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

    Command completion matches based on prefix:

    >>> import unittest.mock
    >>> with unittest.mock.patch('readline.get_line_buffer') as mock_gb:
    ...     mock_gb.return_value = '/c'
    ...     results = [completer('c', i) for i in range(4)]
    >>> sorted(r for r in results if r is not None)
    ['calculate', 'cat', 'compact']

    No completions returned when the input is not a slash command:

    >>> with unittest.mock.patch('readline.get_line_buffer') as mock_gb:
    ...     mock_gb.return_value = 'hello'
    ...     completer('hello', 0) is None
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
    Example 1: Fail when .git is missing
    >>> import os
    >>> _old_isdir = os.path.isdir
    >>> os.path.isdir = lambda path: False
    >>> repl()
    Error: .git folder not found
    >>> os.path.isdir = _old_isdir

    Example 2: Handle an unknown command
    >>> import builtins
    >>> _old_input = builtins.input
    >>> _old_isdir = os.path.isdir
    >>> os.path.isdir = lambda path: True
    >>> os.path.isfile = lambda path: False
    >>> # Simulate typing "/badcmd" then "/exit"
    >>> inputs = iter(["/badcmd", "/exit"])
    >>> builtins.input = lambda _: next(inputs)
    >>> try:
    ...     repl()
    ... except StopIteration:
    ...     pass
    Error: unknown command badcmd
    >>> builtins.input = _old_input
    >>> os.path.isdir = _old_isdir
    
    Example 3: Successful LLM message flow
    >>> class MockChat:
    ...     def __init__(self, **kwargs): self.messages = []
    ...     def send_message(self, text): return "AI: " + text
    >>> _old_chat = Chat
    >>> globals()['Chat'] = MockChat
    >>> inputs = iter(["hello", "/exit"])
    >>> builtins.input = lambda _: next(inputs)
    >>> repl()
    Hello, how can I assist you today?
    >>> builtins.input = _old_input
    >>> globals()['Chat'] = _old_chat
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
                chat.messages.append({"role": "system", "content": f"{cmd} output: {result}"})
                continue

            print(chat.send_message(user_input))

    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    repl()