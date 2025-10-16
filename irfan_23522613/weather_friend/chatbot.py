import os
from ollama import Client
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

# ✅ Connect to Ollama Cloud
client = Client(
    host="https://ollama.com",
    headers={'Authorization': f'Bearer {OLLAMA_API_KEY}'}
)

# 🧠 Minimal conversation memory
conversation_history = [
    {
        "role": "system",
        "content": (
            "You are Weather Friend — a short, funny, and friendly weather chatbot. "
            "Keep replies under 20 words. Be playful but useful. "
            "If asked about something you can’t check live, give a quick general answer like "
            "'Not sure right now, but usually sunny there!'. "
            "Never repeat yourself, never explain, just give one witty response."
        )
    }
]


def talk_to_weather_friend(message: str):
    """Chat with Weather Friend using Ollama Cloud (short, clear replies)."""
    try:
        conversation_history.append({"role": "user", "content": message})

        # Request single response (no streaming)
        response = client.chat("gpt-oss:120b", messages=conversation_history)

        reply = response["message"]["content"].strip()
        conversation_history.append({"role": "assistant", "content": reply})

        return reply  # ✅ only return, don’t print

    except Exception as e:
        return f"⚠️ Error talking to Weather Friend: {e}"
