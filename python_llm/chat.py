import os
import json
import readline
from groq import Groq
from dotenv import load_dotenv

from tools.ls import ls
from tools.cat import cat
from tools.grep import grep
from tools.calculate import calculate
# import compact

# from tools.doctests import doctests
# from tools.write_file import write_file
# from tools.write_files import write_files
# from tools.rm import rm


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
                "content": ("You are a helpful assistant with access to tools.\n"
                "If a user asks about files, directories, or code, you MUST use the appropriate tool (ls, cat, grep).\n"
                "Do NOT guess file contents.\n"
                "All file paths MUST be relative to the current directory.\n"
                "Valid examples: '.', './README.md', 'README.md'.\n"
                "Never use absolute paths like /home or /Users.\n"
                "Paths like 'README.md' are safe and valid.\n"
                "If the user asks about files or directories, you MUST call a tool.\n"
                "Do NOT ask for paths — assume '.' if not provided.\n")
            },
        ]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "ls",
                    "description": "List files in a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "calculates an expression",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "self": {"type": "string"}
                        },
                        "required": ["self"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cat",
                    "description": "Reads and returns the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"}
                        },
                        "required": ["path"]
                    }
                }
            },
            #{
                #"type": "function",
                #"function": {
                    #"name": "compact",
                    #"description": "Summarizes messages",
                    #"parameters": {
                        #"type": "object",
                        #"properties": {
                            #"chat": {"type": "string"}
                        #},
                        #"required": ["chat"]
                    #}
                #}
            #},
            {
                "type": "function",
                "function": {
                    "name": "grep",
                    "description": "Outputs lines with pattern matching",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string"},
                            "path": {"type": "string"}
                        },
                        "required": ["pattern", "path"]
                    }
                }
            }
        ]
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

        for i in range(10):
            while True:
                chat_completion = self.client.chat.completions.create(
                    messages=self.messages,
                    model="llama-3.3-70b-versatile",
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=temperature,
                )
                msg = chat_completion.choices[0].message

                if getattr(msg, "tool_calls", None):
                    self.messages.append(msg)
                    for tool_call in msg.tool_calls:
                        name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        result = self.execute_tool(name, args)
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": name,
                            "content": str(result),
                        })
                    continue
                self.messages.append({
                    "role": "assistant",
                    "content": msg.content
                })

                return msg.content
    
    def execute_tool(self, name, args):
        if name == "ls":
            return ls(args.get("path", "."))
        if name == "cat":
            return cat(args["path"])
        if name == "grep":
            return grep(args["pattern"], args["path"])
        if name == "calculate":
            return calculate(args["self"])
        #if name == "compact":
            #return compact(self)
        raise ValueError(f"Unknown tool: {name}")


COMMANDS = [
    "ls", "cat", "grep", "calculate", "compact",
    "doctests", "write_file", "write_files", "rm"
]


def completer(text, state):
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
        #"compact": lambda *args: compact(*args),

        # # REQUIRED TOOLS
        # "doctests": doctests,
        # "write_file": write_file,
        # "write_files": write_files,
        # "rm": rm,
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
