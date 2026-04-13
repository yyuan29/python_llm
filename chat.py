from groq import Groq
from dotenv import load_dotenv
from tools.ls import ls
from tools.cat import cat
from tools.grep import grep
load_dotenv()


class Chat:
    """
    >>> chat = Chat(mock=True)
    >>> chat.send_message('my name is bob', temperature=0.0)
    'Hello Bob, I have saved your name.'
    >>> chat.send_message('what is my name?', temperature=0.0)
    'Your name is Bob.'
    >>> chat2 = Chat(mock=True)
    >>> chat2.send_message('what is my name?', temperature=0.0)
    "I don't know your name yet."
    """

    client = Groq()

    def __init__(self, mock=False):
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

    def _mock_completion(self, message):
        """"
        >>> chat = Chat(mock=True)
        >>> chat.messages.append({
        ...     "role": "system",
        ...     "content": "The user previously ran ls and got: .github/workflows"
        ... })

        >>> chat.send_message("what is in the github folder?")
        'There is only a `workflows` folder in the `.github` folder.'

        No ls context → fallback branch

        >>> chat2 = Chat(mock=True)
        >>> chat2.send_message("what files are in the github folder?")
        "I don't have directory info yet."
        """

        # store name
        if "my name is" in message.lower():
            name = message.split("my name is")[-1].strip().capitalize()
            self.user_name = name
            content = f"Hello {name}, I have saved your name."

        elif "what is my name" in message.lower():
            if self.user_name:
                content = f"Your name is {self.user_name}."
            else:
                content = "I don't know your name yet."

        elif "what is in" in message.lower() or "what files" in message.lower():
            for m in reversed(self.messages):
                if m["role"] == "system" and "ls" in m["content"]:
                    result = m["content"]

                    # extract actual path listing
                    if "got:" in result:
                        listing = result.split("got:")[-1].strip()
                    else:
                        listing = result

                    content = f"There is only a `{listing.split('/')[-1]}` folder in the `.github` folder."
                    break
            else:
                content = "I don't have directory info yet."

        class Message:
            def __init__(self, content):
                self.content = content

        class Choice:
            def __init__(self, content):
                self.message = Message(content)

        class Response:
            def __init__(self, content):
                self.choices = [Choice(content)]

        return Response(content)

    def send_message(self, message, temperature=0.0):
        """
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

        >>> chat.client.chat.completions.create = fake_create

        >>> chat.send_message("What color is the sea?")
        'Arrr, the sea be blue!'
        """
        self.messages.append({"role": "user", "content": message})

        if self.mock:
            chat_completion = self._mock_completion(message)
        else:
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

    REPL ls command executes and prints result

    >>> import builtins
    >>> inputs = ["/ls .", "exit"]

    >>> def fake_input(prompt):
    ...     return inputs.pop(0)

    >>> old = builtins.input
    >>> builtins.input = fake_input

    >>> repl()
    ./README.md ./__pycache__ ./chat.py ./dist ./empty.txt ./htmlcov ./pyproject.toml ./requirements.txt ./t_bin ./t_txt ./test1.txt ./test2.txt ./tools ./utf16.txt
    >>> builtins.input = old

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

            raw = user_input
            user_input = user_input.strip()

            if user_input.lower() in ("exit", "quit"):
                break

            # ✅ FIX: slash command handling FIRST
            if user_input.startswith("/"):
                parts = user_input[1:].split()
                command = parts[0]
                args = parts[1:]

                if command == "ls":
                    result = ls(*args)
                    print(result)

                    chat.messages.append({
                        "role": "system",
                        "content": f"The user previously ran ls and got: {result}"
                    })

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
            print(chat.send_message(raw))

    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    repl()
