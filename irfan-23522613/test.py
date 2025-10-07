import sys
import requests

def geocode(name: str):
    """Return the first geocoding match (name, country. lat. lon) or None."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": name, "count": 1, "language": "en", "format": "json"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    results = data.get("results") or []
    if not results:
        return None
    c = results[0]
    return {
        "name": c["name"],
        "country": c["country"],
        "lat": c["latitude"],
        "lon": c["longitude"],
    }
    
def get_current_weather(lat: float, lon: float):
    """Fetch weather data from Open-Meteo's newer API structure."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,weathercode",
        "timezone": "auto",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data.get("current", {})

WEATHER_CODE = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense intensity drizzle",
    56: "Light freezing drizzle",
    57: "Dense intensity freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy intensity rain",
    66: "Light freezing rain",
    67: "Heavy intensity freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy intensity snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

def code_text(code):
    try:
        return WEATHER_CODE.get(int(code), f"Code {code}")
    except Exception:
        return str(code)
    
def main():
    city = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else ""
    if not city:
        city = input("Enter city name (e.g., Perth or Sydney): ").strip()
        
    if not city:
        print("No city name provided, exiting.")
        return
    
    try:
        place = geocode(city)
        if not place:
            print(f"No results for '{city}'. Try another name.")
            return
        
        wx = get_current_weather(place["lat"], place["lon"])
        print(wx)
        if not wx:
            print("Could not get weather data. Try again later.")
            return
        
        desc = code_text(wx.get("weathercode"))
        temp = wx.get("temperature_2m")
        wind = wx.get("windspeed_10m") or wx.get("wind_speed") or "N/A"
        time = wx.get("time")
        
        print("\n=== Weather Friend (Terminal) ===")
        print(f"Location: {place['name']}, {place['country']} ({place['lat']:.2f}, {place['lon']:.2f})")
        print(f"Time: {time}")
        print(f"Now: {temp}°C, wind {wind} km/h, {desc}")
        print("=================================\n")
        
    except requests.HTTPError as e:
        print(f"HTTP error: {e}")
    except requests.RequestException as e:
        print(f"Network error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}") 
        
if __name__ == "__main__":
    main()  