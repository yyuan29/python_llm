#!/usr/bin/env python
import os
import argparse
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--url")
parser.add_argument("--apikey")
parser.add_argument("--model", default="llama-3.3-70b-versatile")
parser.add_argument("--port", type=int, default=7860)
args = parser.parse_args()

api_key = args.apikey or os.getenv('GROQ_API_KEY')

client = OpenAI(
    base_url=args.url or "https://api.groq.com/openai/v1",
    api_key=api_key,
)

def chat(message, history):
    import json
    from chat import Chat
    from tools.cat import cat

    bot = Chat()

    messages = [{
        "role": "system",
        "content": "You are a helpful assistant with access to local files."
    }]

    for msg in history:
        if isinstance(msg, dict):
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        else:
            user_msg, assistant_msg = msg
            if user_msg:
                messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})

    messages.append({"role": "user", "content": message})

    if "readme" in message.lower():
        try:
            readme_content = cat("README.md")
            messages.append({
                "role": "system",
                "content": f"Here is the content of README.md:\n{readme_content}"
            })
        except Exception as e:
            messages.append({
                "role": "system",
                "content": f"Could not read README.md: {e}"
            })

    response = client.chat.completions.create(
        model=args.model,
        messages=messages,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    gr.ChatInterface(chat).launch(server_port=args.port)