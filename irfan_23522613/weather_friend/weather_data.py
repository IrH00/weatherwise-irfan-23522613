import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather_data(location, forecast_days=5):
    """Retrieve current weather and forecast for a given city."""
    base_url = "https://api.openweathermap.org/data/2.5/"
    geo_url = f"{base_url}weather?q={location}&appid={API_KEY}&units=metric"

    try:
        geo_response = requests.get(geo_url, timeout=10)
        geo_response.raise_for_status()
        data = geo_response.json()

        lat, lon = data["coord"]["lat"], data["coord"]["lon"]

        # Current weather
        current = {
            "temp": data["main"]["temp"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"]
        }

        # Forecast
        forecast_url = f"{base_url}forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        forecast_response = requests.get(forecast_url, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        return {
            "current": current,
            "forecast": forecast_data
        }

    except Exception as e:
        raise RuntimeError(f"Weather data error: {e}")
