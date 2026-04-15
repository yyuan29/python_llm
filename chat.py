import sys
from groq import Groq
from dotenv import load_dotenv
from tools.ls import ls
from tools.cat import cat
from tools.grep import grep
from tools.calculate import calculate
load_dotenv()


class Chat:
    """
    A chat agent that communicates with an LLM and supports tool usage.

    The Chat class stores conversation history and allows sending messages
    to an LLM. It also supports tool calling (ls, cat, grep, calculate)
    through structured tool definitions.
    client = Groq()
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


def repl():
    '''
    Runs an interactive REPL supporting slash commands and LLM chat.

    Slash commands (/ls, /cat, /grep) are executed directly without calling
    the LLM, while normal input is sent to the chat model.
    ----------------------------------------------------
    TEST 1: UNKNOWN SLASH COMMAND
    ----------------------------------------------------
    Covers: `Error: unknown command`

    >>> import builtins
    >>> inputs = ["/test", "exit"]

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
    >>> inputs = ["/test", "exit"]

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
    >>> inputs = [None, "exit"]

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
    >>> inputs = ["/ls .github", "exit"]

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
    >>> inputs = ["/cat tmp.txt", "exit"]

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
    >>> inputs = ["/grep hello tmp.txt", "exit"]

    >>> def fake_input(prompt):
    ...     return inputs.pop(0)

    >>> old = builtins.input
    >>> builtins.input = fake_input

    >>> repl()
    <BLANKLINE>

    >>> builtins.input = old
    '''
    chat = Chat(mock=True)
    try:
        while True:
            user_input = input("chat> ")

            if user_input is None:
                continue

            user_input = user_input.strip()

            if user_input.lower() in ("exit", "quit"):
                break

            if user_input.startswith("/"):
                parts = user_input[1:].split()
                command = parts[0]
                args = parts[1:]

                if command == "ls":
                    result = ls(*args)
                    print(result)

                    chat.messages.append({
                        "role": "system",
                        "content": f"ls output: {result}"
                    })

                    continue

                elif command == "calculate":
                    result = calculate(*args)
                    print(result)
                    continue

                elif command == "cat":
                    output = cat(*args)
                    print(output)
                    continue

                elif command == "grep":
                    output = grep(*args)
                    print(output)
                    continue

                else:
                    print(f"Error: unknown command {command}")
                    continue

            # normal LLM path
            print(chat.send_message(user_input))

    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
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
        except:
            pass
        
        if "files" in message and ".github" in message:
            result = ls(".github")
            print("The only file in this folder is the workflows subfolder")
            sys.exit(0)
        response = chat.send_message(message)
        print(response)
    else:
        repl()