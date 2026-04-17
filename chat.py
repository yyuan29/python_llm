import readline
import os
import sys
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

    The Chat class stores conversation history and allows sending messages
    to an LLM. It also supports tool calling (ls, cat, grep, calculate)
    through structured tool definitions.
    """

    def __init__(self, mock=False):
        """
        Initializes the chat with default system prompt and tool definitions.
        """
        self.client = Groq()
        self.mock = mock
        self.messages = [
            {
                "role": "system",
                "content": "Respond clearly in 1-2 sentences."
            },
        ]

        self.tools = [
            # these schemas for the tools should be in
            # the same file where the tool function
            # is defined; the general principle
            # is that everything about a function
            # should always be in the same place
            # so that future changes are easier to do
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Evaluate a mathematical expression",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string",
                                           "description":
                                           "The math expression to evaluate"}
                        },
                        "required": ["expression"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "ls",
                    "description": "List files in a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string",
                                     "description": "The directory to list"
                                     "(defaults to '.')"}
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "cat",
                    "description": "Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filepath": {"type": "string",
                                         "description":
                                         "The path to the file"}
                        },
                        "required": ["filepath"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "grep",
                    "description": "Search for a regex pattern"
                    "in files matching a glob",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string",
                                        "description": "Regex pattern"},
                            "path_glob": {"type": "string",
                                          "description": "File path or"
                                          "glob pattern"}
                        },
                        "required": ["pattern", "path_glob"],
                    },
                },
            },
        ]
        self.user_name = None

    def send_message(self, message, temperature=0.0):
        """
        Sends a message to the LLM and returns the assistant's response.

        # these are pretty janky test cases...
        >>> chat = Chat(mock=False)

        >>> class FakeMessage:
        ...     def __init__(self):
        ...         self.content = "Arrr, the sea be blue!"

        >>> class FakeChoice:
        ...     def __init__(self):
        ...         self.message = FakeMessage()

        >>> class FakeResponse:
        ...     choices = [FakeChoice()]

        >>> def fake_create(**kwargs):
        ...     return FakeResponse()

        >>> chat = Chat(mock=False)

        # mock response object
        >>> class FakeMessage:
        ...     def __init__(self):
        ...         self.content = "ok"

        >>> class FakeChoice:
        ...     def __init__(self):
        ...         self.message = FakeMessage()

        >>> class FakeResponse:
        ...     choices = [FakeChoice()]

        # capture what gets passed into the API
        >>> captured = {}
        >>> def fake_create(**kwargs):
        ...     captured["messages"] = kwargs["messages"]
        ...     return FakeResponse()

        >>> chat.client.chat.completions.create = fake_create

        # send message
        >>> chat.send_message("hello")
        'ok'

        # test 1: message was appended
        >>> chat.messages[-2]["content"]
        'hello'

        # test 2: API received updated messages
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
    '''
    explain the purpose;
    this function should be relatively easy to write
    high quality test cases for as well
    '''
    buffer = readline.get_line_buffer()
    parts = buffer.split()

    # 1. COMPLETING COMMANDS (If we haven't typed a space yet)
    if len(parts) <= 1:
        # We only care about what comes after the slash
        cmd_prefix = text.lstrip('/')
        matches = [
            c for c in COMMANDS
            if c.startswith(cmd_prefix)
        ]
        return matches[state] if state < len(matches) else None

    # 2. COMPLETING PATHS (If we have typed a space, e.g., "/ls .g")
    else:
        # text is the current word being completed (e.g., ".g")
        # We look in the directory provided by 'text'
        dirname = os.path.dirname(text) or "."
        basename = os.path.basename(text)

        try:
            entries = os.listdir(dirname)
        except OSError:
            return None

        matches = []
        for entry in entries:
            if entry.startswith(basename):
                # We return the full path relative to the input
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
    >>> inputs = ["/test", "/exit"/g]

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
    >>> inputs = ["/test", "/exit"/g]

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
    >>> inputs = [None, "/exit"/g]

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
    >>> inputs = ["/ls .github", "/exit"/g]

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
    >>> inputs = ["/cat tmp.txt", "/exit"/g]

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
    >>> inputs = ["/grep hello tmp.txt", "/exit"/g]

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
    try:
        while True:
            user_input = input("chat> ")

            if user_input is None:
                continue

            user_input = user_input.strip()

            if user_input.lower() in ("/exit"/g, "/quit"/g):
                break

            if user_input.startswith("/"):
                parts = user_input[1:].split()
                command = parts[0]
                args = parts[1:]

                if command == "ls":
                    result = ls(*args)
                    # why is only ls output being appended here but not any of the other functions?
                    # the llm won't be able to see any of their outputs,
                    # and so won't be able to answer questions based on the output
                    # I've modified the code to be a bit cleaner (and correct),
                    # but you could do even better using a dictionary to map the strings to function calls
                    # like they do in the tutorial
                elif command == "calculate":
                    result = calculate(*args)
                elif command == "cat":
                    result = cat(*args)
                elif command == "grep":
                    result = grep(*args)
                elif command == "compact":
                    result = compact(chat)
                else:
                    print(f"Error: unknown command {command}")
                    continue
                print(result)
                chat.messages.append({
                    "role": "system",
                    "content": f"ls output: {result}"
                })

            # normal LLM path
            print(chat.send_message(user_input))

    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    # better to use argparse to get the command line args
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        chat = Chat()

        # give model context from README
        try:
            readme = cat("README.md")
            chat.messages.append({
                "role": "system",
                "content": f"Here is the README:\n{readme}"
            })
        except FileNotFoundError:
            pass
        # hardcoding responses is not correct
        response = chat.send_message(message)
        print(response)
    else:
        repl()
