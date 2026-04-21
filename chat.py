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
        self.tools = []
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

        >>> def fake_create(**kwargs):
        ...     return FakeResponse()

        >>> chat.client.chat.completions.create = fake_create

        # basic response
        >>> chat.send_message("hello")
        'ok'

        # user message is stored
        >>> chat.messages[-2]["role"]
        'user'
        >>> chat.messages[-2]["content"]
        'hello'

        # assistant message is stored
        >>> chat.messages[-1]["role"]
        'assistant'
        >>> chat.messages[-1]["content"]
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


COMMANDS = [
    "ls", "cat", "grep", "calculate", "compact",
    "doctests", "write_file", "write_files", "rm"
]


def completer(text, state):
    """
    This allows you to tab complete. 
    >>> # Completes CLI input: suggests matching commands when typing a "/" prefix
    >>> readline.get_line_buffer = lambda: "/l"
    >>> completer("/l", 0) in ["ls"]
    True

    >>> # Returns multiple matching commands for a given prefix
    >>> readline.get_line_buffer = lambda: "/c"
    >>> completer("/c", 0) in ["cat", "calculate"]
    True
    >>> completer("/c", 1) in ["cat", "calculate"]
    True

    >>> # Returns None when no commands match the prefix
    >>> readline.get_line_buffer = lambda: "/zzz"
    >>> completer("/zzz", 0) is None
    True

    >>> # Completes filesystem paths by listing matching directory entries
    >>> readline.get_line_buffer = lambda: "."
    >>> isinstance(completer(".", 0), (str, type(None)))
    True
    """
    buffer = readline.get_line_buffer()
    parts = buffer.split()

    # Command completion
    if len(parts) <= 1:
        cmd_prefix = text.lstrip('/')
        matches = [c for c in COMMANDS if c.startswith(cmd_prefix)]
        return matches[state] if state < len(matches) else None

    # Path completion
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
    '''
    Runs an interactive REPL supporting slash commands and LLM chat.

    Slash commands (/ls, /cat, /grep) are executed directly without calling
    the LLM, while normal input is sent to the chat model.
    ----------------------------------------------------
    TEST 1: UNKNOWN SLASH COMMAND
    ----------------------------------------------------
    Covers: `Error: unknown command`

    # an "/exit"/g command is a reasonable way to support
    # leaving the repl; but it should be /exit
    # to line up with all of your other slash commands
    >>> import builtins
    >>> inputs = ["/test", "/exit"]

    >>> def fake_input(prompt):
    ...     return inputs.pop(0)

    >>> old_input = builtins.input
    >>> builtins.input = fake_input

    >>> repl()
    Error: unknown command test

    >>> builtins.input = old_input


    ----------------------------------------------------
    TEST 2: SECOND UNKNOWN COMMAND (redundant coverage)
    ----------------------------------------------------
    Ensures consistent behavior for repeated unknown commands

    >>> import builtins
    >>> inputs = ["/test", "/exit"]

    >>> def fake_input(prompt):
    ...     return inputs.pop(0)

    >>> old_input = builtins.input
    >>> builtins.input = fake_input

    >>> repl()
    Error: unknown command test

    >>> builtins.input = old_input


    ----------------------------------------------------
    TEST 3: KEYBOARD INTERRUPT HANDLING
    ----------------------------------------------------
    Covers: KeyboardInterrupt / EOFError cleanup

    >>> import builtins
    >>> def fake_input(prompt):
    ...     raise KeyboardInterrupt()

    >>> old = builtins.input
    >>> builtins.input = fake_input

    >>> repl()
    <BLANKLINE>

    >>> builtins.input = old

    ----------------------------------------------------
    TEST 4: None Input
    ----------------------------------------------------

    Covers None input branch in REPL

    >>> import builtins
    >>> inputs = [None, "/exit"]

    >>> def fake_input(prompt):
    ...     return inputs.pop(0)

    >>> old = builtins.input
    >>> builtins.input = fake_input

    >>> repl()

    >>> builtins.input = old

    ----------------------------------------------------
    TEST 5: LS COMMAND
    ----------------------------------------------------

    REPL ls command executes and prints result

    >>> import builtins
    >>> inputs = ["/ls .github", "/exit"]

    >>> def fake_input(prompt):
    ...     return inputs.pop(0)

    >>> old = builtins.input
    >>> builtins.input = fake_input

    >>> repl()
    .github/workflows
    >>> builtins.input = old

    ----------------------------------------------------
    TEST 6: CAT COMMAND (FILE NOT FOUND)
    ----------------------------------------------------

    REPL cat command executes correctly

    >>> import builtins
    >>> inputs = ["/cat tmp.txt", "/exit"]

    >>> def fake_input(prompt):
    ...     return inputs.pop(0)

    >>> old = builtins.input
    >>> builtins.input = fake_input

    >>> repl()
    Error: File 'tmp.txt' not found.

    >>> builtins.input = old

    ----------------------------------------------------
    TEST 6: GREP COMMAND (NO MATCH)
    ----------------------------------------------------

    REPL grep command executes correctly

    >>> import builtins
    >>> inputs = ["/grep hello tmp.txt", "/exit"]

    >>> def fake_input(prompt):
    ...     return inputs.pop(0)

    >>> old = builtins.input
    >>> builtins.input = fake_input

    >>> repl()
    <BLANKLINE>

    >>> builtins.input = old
    '''
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    chat = Chat(mock=True)

    # ✅ STARTUP CHECKS (REQUIRED)
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

        # REQUIRED TOOLS
        "doctests": doctests,
        "write_file": write_file,
        "write_files": write_files,
        "rm": rm,
    }

    try:
        while True:
            user_input = input("chat> ")

            if user_input is None:
                continue

            user_input = user_input.strip()

            if user_input.lower() in ("/exit", "/quit"):
                break

            # -------------------------
            # COMMAND MODE
            # -------------------------
            if user_input.startswith("/"):
                parts = user_input[1:].split()

                if len(parts) == 0:
                    print("Error: unknown command")
                    continue

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

            # -------------------------
            # SMART DIRECTORY EXPLAIN
            # -------------------------
            if "/" in user_input:
                try:
                    structure = ls(user_input.split()[-1])
                    prompt = f"""
This is a directory listing:

{structure}

Explain what this project/folder is about.
"""
                    print(chat.send_message(prompt))
                except Exception:
                    print(chat.send_message(user_input))
            else:
                print(chat.send_message(user_input))

    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    repl()
