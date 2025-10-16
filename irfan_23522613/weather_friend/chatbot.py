import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_API_URL = "https://api.ollama.ai/v1/chat/completions"

def talk_to_weather_friend(user_message):
    """
    Send user message to Ollama Cloud and return AI response.
    """
    if not OLLAMA_API_KEY:
        return "❌ Missing OLLAMA_API_KEY in .env file."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OLLAMA_API_KEY}"
    }

    payload = {
        "model": "llama3.1",  # You can change this to another supported model
        "messages": [
            {"role": "system", "content": "You are Weather Friend, a friendly weather chatbot. Answer clearly and conversationally."},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error talking to Weather Friend: {e}"
