import os
import readline
from groq import Groq
from dotenv import load_dotenv
from tools.ls import ls
from tools.cat import cat
from tools.grep import grep
from tools.calculate import calculate
from tools.compact import compact

load_dotenv()


class Chat:
    """
    A chat agent that communicates with an LLM and supports tool usage.
    """

    def __init__(self, mock=False):
        self.client = Groq()
        self.mock = mock
        self.messages = [
            {
                "role": "system",
                "content": "Respond clearly in 1-2 sentences."
            },
        ]

        self.tools = []  # (kept simple since you're not using tool calling here)
        self.user_name = None

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

        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model="llama-3.1-8b-instant",
            temperature=temperature,
        )

        result = chat_completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": result})
        return result


COMMANDS = ["ls", "cat", "grep", "calculate", "compact"]


def completer(text, state):
    """
    Autocomplete function for the REPL.

    - Completes slash commands like /ls, /cat, etc.
    - Completes file paths after a command (e.g., /ls .git)
    """
    buffer = readline.get_line_buffer()
    parts = buffer.split()

    if len(parts) <= 1:
        cmd_prefix = text.lstrip('/')
        matches = [c for c in COMMANDS if c.startswith(cmd_prefix)]
        return matches[state] if state < len(matches) else None

    dirname = os.path.dirname(text) or "."
    basename = os.path.basename(text)

    try:
        entries = os.listdir(dirname)
    except OSError:
        return None

    matches = []
    for entry in entries:
        if entry.startswith(basename):
            full_path = os.path.join(dirname, entry)
            if os.path.isdir(full_path):
                full_path += "/"
            matches.append(full_path)

    return matches[state] if state < len(matches) else None


def repl():
    """
    Runs an interactive REPL supporting slash commands and LLM chat.

    ----------------------------------------------------
    TEST 1: UNKNOWN COMMAND
    ----------------------------------------------------
    >>> import builtins
    >>> inputs = ["/test", "/exit"]
    >>> def fake_input(_):
    ...     return inputs.pop(0)
    >>> old = builtins.input
    >>> builtins.input = fake_input
    >>> repl()
    Error: unknown command test
    >>> builtins.input = old

    ----------------------------------------------------
    TEST 2: KEYBOARD INTERRUPT
    ----------------------------------------------------
    >>> import builtins
    >>> def fake_input(_):
    ...     raise KeyboardInterrupt()
    >>> old = builtins.input
    >>> builtins.input = fake_input
    >>> repl()
    <BLANKLINE>
    >>> builtins.input = old

    ----------------------------------------------------
    TEST 3: NONE INPUT
    ----------------------------------------------------
    >>> import builtins
    >>> inputs = [None, "/exit"]
    >>> def fake_input(_):
    ...     return inputs.pop(0)
    >>> old = builtins.input
    >>> builtins.input = fake_input
    >>> repl()
    >>> builtins.input = old
    """
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    chat = Chat(mock=True)

    command_map = {
        "ls": ls,
        "cat": cat,
        "grep": grep,
        "calculate": calculate,
        "compact": lambda *args: compact(chat),
    }

    try:
        while True:
            user_input = input("chat> ")

            if user_input is None:
                continue

            user_input = user_input.strip()

            if user_input.lower() in ("/exit", "/quit"):
                break

            if user_input.startswith("/"):
                parts = user_input[1:].split()
                command = parts[0]
                args = parts[1:]

                if command not in command_map:
                    print(f"Error: unknown command {command}")
                    continue

                try:
                    result = command_map[command](*args)
                except Exception as e:
                    result = f"Error: {str(e)}"

                print(result)

                chat.messages.append({
                    "role": "system",
                    "content": f"{command} output: {result}"
                })

                continue

            print(chat.send_message(user_input))

    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    repl()