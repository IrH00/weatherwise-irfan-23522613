import sys
import requests
API_KEY = "e6a2841079bca486e90d927f5357fc35"

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
    """Use OpenWeatherMap Current Weather API to get reliable temperature, wind, and condition data."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data

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
    print("\n=== Weather Friend ===")
    print("Type a city name (e.g., Perth or Sydney)")
    print("Type 'q' or 'exit' to quit.\n")
    
    while True:
        city = input("Enter City: ").strip()
        if city.lower() in {"q", "quit", "exit"}:
            print("Goodbye! Stay Weather-Wise ;)")
            break
        
        try:
            place = geocode(city)
            if not place:
                print(f"No results for '{city}'. Try another name.\n")
                continue
            
            wx = get_current_weather(place["lat"], place["lon"])
            if not wx:
                print("Could not get weather data. Try again later.\n")
                continue
            
            temp = wx["main"]["temp"]
            wind = wx["wind"]["speed"]
            desc = wx["weather"][0]["description"].title()
            time = wx.get("dt")
        
            from datetime import datetime
            time = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M UTC') if time else "Unknown time"
            
            print("\n----------------------")
            print(f"Location: {place['name']}, {place['country']} ({place['lat']:.2f}, {place['lon']:.2f})")
            print(f"Time: {time}")
            print(f"Now: {temp}°C, wind {wind} km/h, {desc}")
            print("------------------------\n")
            
        except requests.HTTPError as e:
            print(f"HTTP error: {e}")
        except requests.RequestException as e:
            print(f"Network error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    
        
if __name__ == "__main__":
    main()  