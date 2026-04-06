import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

class Chat:
    """
    >>> chat = Chat(mock=True)
    >>> chat.send_message('my name is bob', temperature=0.0)
    'Arrr, ye be Bob, eh? Yer name be known to me now, matey.'
    >>> chat.send_message('what is my name?', temperature=0.0)
    "Ye be askin' about yer own name, eh? Yer name be... Bob, matey!"
    >>> chat2 = Chat(mock=True)
    >>> chat2.send_message('what is my name?', temperature=0.0)
    "Arrr, I be not aware o' yer name, matey."
    """

    client = Groq()

    def __init__(self, mock=False):
        self.mock = mock
        self.messages = [
            {
                "role": "system",
                "content": "Write the output in 1-2 sentences. Talk like pirate."
            },
        ]
        self.user_name = None

    def _mock_completion(self, message):
        """Return deterministic pirate responses for testing."""
        if "my name is" in message.lower():
            name = message.split("my name is")[-1].strip().capitalize()
            self.user_name = name
            content = f"Arrr, ye be {name}, eh? Yer name be known to me now, matey."
        elif "what is my name" in message.lower():
            if self.user_name:
                content = f"Ye be askin' about yer own name, eh? Yer name be... {self.user_name}, matey!"
            else:
                content = "Arrr, I be not aware o' yer name, matey."
        else:
            content = "Arrr, a sneaky little monkey, eh? Ye be swingin' into our conversation, matey!"

        # Return **instances** like the real API
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
    >>> def monkey_input(prompt, user_inputs=['Hello, I am monkey.', 'Goodbye.']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl()
    chat> Hello, I am monkey.
    Arrr, a sneaky little monkey, eh? Ye be swingin' into our conversation, matey!
    chat> Goodbye.
    Arrr, a sneaky little monkey, eh? Ye be swingin' into our conversation, matey!
    <BLANKLINE>
    '''
    import readline
    chat = Chat(mock=True)
    try:
        while True:
            user_input = input("chat> ")
            response = chat.send_message(user_input)
            print(response)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    repl()