from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env automatically


def compact(chat):
    """
    Summarize chat.messages into 1–5 lines and replace chat history
    with a single system summary message.
    """

    # API key is automatically loaded from .env
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Build summarization prompt
    summary_messages = [
        {
            "role": "system",
            "content": (
                "You are a chat summarizer. "
                "Summarize the conversation into 1–5 concise lines. "
                "Keep key facts, tool outputs, and user intent. "
                "Remove unnecessary detail."
            ),
        },
        {
            "role": "user",
            "content": str(chat.messages),
        },
    ]

    # Call LLM
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=summary_messages,
    )

    summary = response.choices[0].message.content

    # Replace full history with compacted memory
    chat.messages = [
        {
            "role": "system",
            "content": f"Conversation summary:\n{summary}",
        }
    ]

    return summary