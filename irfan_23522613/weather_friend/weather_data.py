import os
import requests
from dotenv import load_dotenv

# Load environment variables (for your API key)
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather_data(city, forecast_days=5):
    """
    Retrieve weather data for a specified location using OpenWeatherMap API.

    Args:
        city (str): City or location name.
        forecast_days (int): Number of forecast days (1–5).

    Returns:
        dict: Contains city info and forecast data.
    """
    if not API_KEY:
        raise EnvironmentError("Missing OPENWEATHER_API_KEY in .env file.")

    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "cnt": forecast_days * 8  # 8 readings per day (3-hour intervals)
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Ensure API returned valid structure
        if "list" not in data or not data["list"]:
            raise ValueError(f"No forecast data returned for city: {city}")

        # Wrap into a consistent structure for main.py
        formatted = {
            "city": data.get("city", {"name": city}),
            "list": data["list"]
        }

        return formatted

    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP error: {e}")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Network error: Unable to connect to weather API.")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")
