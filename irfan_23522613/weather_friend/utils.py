from rich.console import Console

console = Console()

def print_header(title):
    """Prints a consistent styled header panel."""
    console.rule(f"[bold cyan]{title}[/bold cyan]")

def error_message(msg):
    console.print(f"[red]❌ {msg}[/red]")

def success_message(msg):
    console.print(f"[green]✅ {msg}[/green]")

import re
from datetime import datetime, timedelta

def parse_weather_question(question: str):
    """Extracts city and forecast time from natural language queries."""
    question = question.lower()
    city = None
    days = 1

    # match e.g. "in perth", "for tokyo", "at london"
    city_match = re.search(r"(?:in|for|at)\s+([a-zA-Z\s]+?)(?:\s+(?:today|tomorrow|next|now))?$", question)
    if city_match:
        city = city_match.group(1).strip()

    # detect time frame
    if "tomorrow" in question:
        days = 2
    elif "next" in question or "five" in question or "5" in question:
        days = 5
    elif "three" in question or "3" in question:
        days = 3
    elif "two" in question or "2" in question:
        days = 2
    else:
        days = 1

    return {"location": city, "days": days}


def generate_weather_response(parsed, data):
    """Formats a friendly short response from weather data."""
    if not data or "current" not in data:
        return "⚠️ Sorry, I couldn't fetch the weather for that location."

    current = data["current"]
    city = data.get("city", "that place").title()
    temp = current.get("temp", "—")
    desc = current.get("description", "unknown").title()
    humidity = current.get("humidity", "—")
    wind = current.get("wind_speed", "—")

    # Add quick witty tone
    return (
        f"🌤 {city}: {desc}, {temp}°C — humidity {humidity}% and wind {wind} m/s. "
        f"Looks {'great' if temp > 20 else 'chilly'} out there!"
    )
