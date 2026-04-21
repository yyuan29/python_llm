from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()


def compact(chat):
    """
    Summarize chat.messages into 1–5 concise lines and replace
    history with a compressed version while preserving system rules.
    >>> import types
    >>> from tools.compact import compact

    >>> class FakeChat:
    ...     def __init__(self):
    ...         self.messages = [
    ...             {"role": "system", "content": "rules"},
    ...             {"role": "user", "content": "hi"}
    ...         ]

    >>> class FakeMsg:
    ...     content = "summary"

    >>> class FakeChoice:
    ...     message = FakeMsg()

    >>> class FakeResp:
    ...     choices = [FakeChoice()]

    >>> # mock Groq client
    >>> import tools.compact as c
    >>> c.Groq = lambda api_key=None: types.SimpleNamespace(
    ...     chat=types.SimpleNamespace(
    ...         completions=types.SimpleNamespace(create=lambda **k: FakeResp())
    ...     )
    ... )

    >>> chat = FakeChat()

    >>> compact(chat)
    'summary'

    >>> len(chat.messages) >= 2
    True
    """

    # Use API key from environment
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Preserve original system prompt (IMPORTANT)
    original_system = None
    if chat.messages and chat.messages[0]["role"] == "system":
        original_system = chat.messages[0]

    summary_messages = [
        {
            "role": "system",
            "content": (
                "You are a conversation summarizer. "
                "Summarize the dialogue into 1–5 concise lines. "
                "Preserve key facts, tool outputs, and user intent. "
                "Remove unnecessary detail."
            ),
        },
        {
            "role": "user",
            "content": str(chat.messages),
        },
    ]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=summary_messages,
    )

    summary = response.choices[0].message.content

    # Rebuild chat history safely
    new_messages = []

    # keep system prompt if it exists
    if original_system:
        new_messages.append(original_system)

    # add compacted memory
    new_messages.append({
        "role": "system",
        "content": f"Conversation summary:\n{summary}",
    })

    chat.messages = new_messages

    return summary
