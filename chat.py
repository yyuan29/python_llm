import os
from groq import Groq

from dotenv import load_dotenv
load_dotenv()

# in pytohn class names are in CamelCase;
# non-class names (e.g. functions/variables) are in snake_case
class Chat:
    '''
    >>> chat = Chat() 
    >>> chat.send_message('my name is bob', temperature=0.0)
    '''
    client = Groq()
    def __init__(self):
        self.messages = [
                {
                    # most important content for sys prompt is length of response
                    "role": "system",
                    "content": "Write the output in 1-2 sentences."
                },
            ]
    def send_message(self, message, temperature=0.8):
        self.messages.append(
            {
                'role': 'user',
                'content': message
            }
        )
        # in order to make non-deterministic code determinsitic;
        # in general very hard CS problem;
        # in this case, has a "temperature" param that controsl randomness;
        # the higher the value, the more randomness;
        # higher temperature => more creativity
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model="llama-3.1-8b-instant",
            temperature=temperature
        )
        result = chat_completion.choices[0].message.content
        self.messages.append({
            'role': 'assistant',
            'content': result
        })
        return result
    
if __name__ == '__main__':
    import readline
    chat = Chat() 
    while True:
        try: 
            user_input = input('chat> ')
            response = chat.send_message(user_input)
            print(response)
        except KeyboardInterrupt: 
            print()
'''
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),  # This is the default and can be omitted
)

chat_completion = client.chat.completions.create(
    # messages is the most important thing to modify
    messages=[
        {
            # most important content for sys prompt is length of response
            "role": "system",
            "content": "Write the output in 1-2 sentences."
        },
        {
            "role": "user",
            "content": "Explain the importance of low latency LLMs",
        }
    ],
    # 2nd most important thing to modify is the model;
    # different models good at different tasks
    # it's tempting to always use best model llama-3.3-70b-versatile
    # but that's bad practice; why?
    model="llama-3.1-8b-instant",
)
print(chat_completion.choices[0].message.content)
'''