import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"


def get_weather_data(city: str, days: int = 1):
    """
    Fetch 5-day / 3-hour forecast from OpenWeather.
    Returns structured data with wind, humidity, and temp.
    """
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        r = requests.get(BASE_URL_FORECAST, params=params, timeout=10)

        if r.status_code != 200:
            return {"error": f"Couldn't find '{city}'. Please check spelling."}

        data = r.json()
        forecast = []

        for item in data.get("list", []):
            main = item.get("main", {})
            weather = (item.get("weather") or [{}])[0]
            wind = item.get("wind", {})
            forecast.append({
                "time": item.get("dt_txt"),
                "temp": main.get("temp"),
                "humidity": main.get("humidity"),
                "wind_speed": wind.get("speed", "—"),
                "description": weather.get("description", "Unknown"),
            })

        # ✅ Limit to chosen number of days (8 slots ≈ 1 day)
        limit = min(days * 8, len(forecast))
        forecast = forecast[:limit]

        # ✅ Extract a single "current" snapshot
        current = {}
        if forecast:
            first = forecast[0]
            current = {
                "temp": first.get("temp"),
                "humidity": first.get("humidity"),
                "wind_speed": first.get("wind_speed"),
                "description": first.get("description").title(),
            }

        city_name = (data.get("city") or {}).get("name", city)
        return {
            "city": city_name,
            "current": current,
            "forecast": forecast,
        }

    except Exception as e:
        return {"error": f"⚠️ Weather data fetch error: {e}"}
