import os
from ollama import Client
from dotenv import load_dotenv
from irfan_23522613.weather_friend.utils import parse_weather_question, generate_weather_response
from irfan_23522613.weather_friend.weather_data import get_weather_data

load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

client = Client(
    host="https://ollama.com",
    headers={'Authorization': f'Bearer {OLLAMA_API_KEY}'}
)

conversation_history = [
    {
        "role": "system",
        "content": (
            "You are Weather Friend — a short, funny, and friendly weather chatbot. "
            "You can use real weather data if available. Keep replies under 25 words. "
            "If the live data is missing, make a witty and plausible weather remark."
        )
    }
]


def talk_to_weather_friend(message: str):
    """Hybrid chatbot — uses weather API if possible, else witty fallback."""
    try:
        # --- Step 1: parse message for city and day ---
        parsed = parse_weather_question(message)
        city = parsed.get("location")
        days = parsed.get("days", 1)

        # --- Step 2: Try getting real weather data ---
        if city:
            try:
                weather_data = get_weather_data(city, days)
                if weather_data:
                    reply = generate_weather_response(parsed, weather_data)
                    if reply:
                        return reply
            except Exception as e:
                print(f"[Weather API error] {e}")

        # --- Step 3: Otherwise, fallback to Ollama witty chat ---
        conversation_history.append({"role": "user", "content": message})
        response = client.chat("gpt-oss:120b", messages=conversation_history)
        reply = response["message"]["content"].strip()
        conversation_history.append({"role": "assistant", "content": reply})
        return reply

    except Exception as e:
        return f"⚠️ Error talking to Weather Friend: {e}"
