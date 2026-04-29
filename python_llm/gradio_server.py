#!/usr/bin/env python
'''
A bare-bones web interface for conversations with LLMs served from openai-compatible endpoints.
'''

import argparse
import os
import gradio as gr
from openai import OpenAI
from chat import Chat
import json

parser = argparse.ArgumentParser()
parser.add_argument("--url")
parser.add_argument("--apikey")
parser.add_argument("--model", default='llama-3.3-70b-versatile')
parser.add_argument("--port", type=int, default=7860)
args = parser.parse_args()

api_key = os.getenv("GROQ_API_KEY")
client = OpenAI(
    base_url=args.url or "http://127.0.0.1:8000/v1",
        api_key="dummy"
)

def chat(message, history):
    messages = []

    for item in history:
        if not isinstance(item, (list, tuple)):
            continue

        if len(item) >= 1 and item[0]:
            messages.append({"role": "user", "content": item[0]})

        if len(item) >= 2 and item[1]:
            messages.append({"role": "assistant", "content": item[1]})

    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=args.model,
        messages=messages,
    )

    if not response or not response.choices:
        return "Error: no response from server"

    return response.choices[0].message.content or ''

gr.ChatInterface(chat).launch(server_port=args.port)
