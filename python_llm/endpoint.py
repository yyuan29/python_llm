'''
A basic openai-compatible endpoint for servering model responses.

The existing "model" just counts the number of times that the user has input a message.
'''

from groq import Groq
from groq import BadRequestError
import os
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import Request
import uvicorn
from chat import Chat

app = FastAPI()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.api_route("/", methods=["GET", "POST"], response_class=HTMLResponse)
async def english():
    return 'hello world\n'

@app.api_route("/spanish", methods=["GET", "POST"], response_class=HTMLResponse)
async def spanish():
    return 'hola mundo\n'

@app.api_route("/latin", methods=["GET", "POST"], response_class=HTMLResponse)
async def latin():
    return 'salve munde\n'

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    bot = Chat()

    for m in messages:
        if m["role"] in ["user", "assistant"]:
            bot.messages.append(m)
    
    try:
        user_msg = messages[-1]["content"] if messages else ""

        result = bot.send_message(user_msg)

    except Exception as e:
        print("SERVER ERROR:", str(e))
        result = f"Error: {str(e)}"

    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 0,
        "model": body.get("model"),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result,
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
