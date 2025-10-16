import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY", "e6a2841079bca486e90d927f5357fc35")

def get_weather_data(location, forecast_days=5):
    """
    Retrieve current weather and forecast data for a specified location.
    Returns both 'current' and 'forecast' dictionaries.
    """
    try:
        # Step 1: Geocode the city name
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {"q": location, "limit": 1, "appid": API_KEY}
        geo_response = requests.get(geo_url, params=geo_params, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        if not geo_data:
            raise ValueError(f"City '{location}' not found.")
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # Step 2: Current weather
        current_url = "https://api.openweathermap.org/data/2.5/weather"
        current_params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
        current_response = requests.get(current_url, params=current_params, timeout=10)
        current_response.raise_for_status()
        current = current_response.json()

        current_data = {
            "temp": current["main"]["temp"],
            "feels_like": current["main"]["feels_like"],
            "humidity": current["main"]["humidity"],
            "wind_speed": current["wind"]["speed"],
            "description": current["weather"][0]["description"],
            "time": datetime.fromtimestamp(current["dt"]).strftime("%Y-%m-%d %H:%M"),
        }

        # Step 3: Forecast
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        forecast_params = {
            "lat": lat,
            "lon": lon,
            "cnt": int(forecast_days) * 8,  # 8 entries per day (3-hour steps)
            "appid": API_KEY,
            "units": "metric",
        }
        forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        return {"current": current_data, "list": forecast_data["list"]}

    except Exception as e:
        raise RuntimeError(f"Weather data fetch error: {e}")
