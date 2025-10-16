import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather_data(location, forecast_days=5):
    """Retrieve weather and forecast data for a specified location."""
    geocode_url = "http://api.openweathermap.org/geo/1.0/direct"
    geo_params = {"q": location, "limit": 1, "appid": API_KEY}
    
    geo_res = requests.get(geocode_url, params=geo_params, timeout=10)
    geo_res.raise_for_status()
    geo_data = geo_res.json()
    if not geo_data:
        raise ValueError(f"City '{location}' not found.")
    
    lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]

    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
    res = requests.get(forecast_url, params=params, timeout=10)
    res.raise_for_status()

    data = res.json()
    return data
