#------Imports-------
import sys
import requests
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box
import time
from datetime import datetime
from halo import Halo
import pandas as pd
import matplotlib.pyplot as plt
import pyinputplus as pyip

#------API setup------
console = Console()
API_KEY = "e6a2841079bca486e90d927f5357fc35"

#------Geocode--------
def geocode(name: str):
    """Convert city name to coordinates using OpenWeatherMap's direct geocoding API."""
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": name, "limit": 1, "appid": API_KEY}
    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        c = data[0]
        return {
            "name": c["name"],
            "country": c.get("country", "Unknown"),
            "lat": c["lat"],
            "lon": c["lon"],
        }
    except requests.exceptions.Timeout:
        console.print("[yellow]⏳ City lookup timed out.[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]Geocoding error: {e}[/red]")
        return None

#-------Current Weather-------
def get_current_weather(lat: float, lon: float):
    """Fetch live current weather conditions."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        time_str = datetime.fromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M")
        return {
            "temp": data["main"]["temp"],
            "wind": data["wind"]["speed"],
            "desc": data["weather"][0]["description"].title(),
            "time": time_str
        }
    except Exception as e:
        console.print(f"[red]Weather fetch error: {e}[/red]")
        return None

#-------Get Forecast-------
def get_forecast(lat: float, lon: float):
    """Fetch 5-day / 3-hour forecast from OpenWeatherMap."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        forecast_list = data["list"]

        # Build DataFrame
        df = pd.DataFrame([
            {
                "time": item["dt_txt"],
                "temp": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "wind": item["wind"]["speed"],
            }
            for item in forecast_list
        ])
        df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
        return df

    except Exception as e:
        console.print(f"[red]Forecast error: {e}[/red]")
        return None

#-------Forecast-------
def plot_forecast(df, city_name):
    """Show temperature and humidity forecast using Matplotlib GUI window and save image."""
    df = df.copy()
    df["time_str"] = df["time"].dt.strftime("%d/%m %H:%M")

    # Style and figure
    plt.style.use("seaborn-v0_8-darkgrid")
    plt.figure(figsize=(10, 5))
    plt.plot(df["time_str"], df["temp"], label="Temperature (°C)", linewidth=2, color="red")
    plt.plot(df["time_str"], df["humidity"], label="Humidity (%)", linewidth=2, color="blue")

    plt.title(f"5-Day Forecast for {city_name}")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.xticks(rotation=45, fontsize=8)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()
    
#-------Custom Menu-------
def menu_input(options):
    """Custom menu input without duplicate prints."""
    valid_choices = {str(i+1): opt for i, opt in enumerate(options)}
    while True:
        choice = input("\nEnter choice [1-4]: ").strip()
        if choice in valid_choices:
            return valid_choices[choice]
        console.print("[red]Invalid choice! Please enter 1–4.[/red]")

#-------Main Menu-------
def main():
    console.print(Panel.fit("🌦️ [bold cyan] Weather Friend[/bold cyan] 🌦️", box=box.DOUBLE))
    console.print("[green]Welcome to your smart weather assistant![/green]\n")

    while True:
        console.print(Panel.fit(
            "[bold white]1.[/bold white] Current Weather\n"
            "[bold white]2.[/bold white] 5-Day Forecast\n"
            "[bold white]3.[/bold white] Help\n"
            "[bold white]4.[/bold white] Exit",
            title="[cyan]Main Menu[/cyan]",
            box=box.ROUNDED,
        ))

        choice = menu_input(["Current Weather", "5-Day Forecast", "Help", "Exit"])

        # ---------- Option 1: Current Weather ----------
        if choice == "Current Weather":
            city = Prompt.ask("[bold white]Enter city[/bold white]")
            spinner = Halo(text=f"Fetching current weather for {city}...", spinner="dots")
            spinner.start()
            try:
                place = geocode(city)
                if not place:
                    spinner.stop()
                    console.print(f"[red]❌ City '{city}' not found. Try again.[/red]\n")
                    continue
                wx = get_current_weather(place["lat"], place["lon"])
                spinner.stop()
                if not wx:
                    console.print("[red]⚠️ Could not get weather data.[/red]\n")
                    continue

                table = Table(title=f"{place['name']}, {place['country']}", box=box.ROUNDED)
                table.add_column("Attribute", style="cyan", no_wrap=True)
                table.add_column("Value", style="bold white")
                table.add_row("Time", wx["time"])
                table.add_row("Temperature", f"{wx['temp']}°C")
                table.add_row("Wind", f"{wx['wind']} m/s")
                table.add_row("Condition", wx["desc"])
                console.print(table)
                console.print()
            except Exception as e:
                spinner.stop()
                console.print(f"[red]Error:[/red] {e}")

        # ---------- Option 2: 5-Day Forecast ----------
        elif choice == "5-Day Forecast":
            city = Prompt.ask("[bold white]Enter city[/bold white]")
            spinner = Halo(text=f"Fetching 5-day forecast for {city}...", spinner="dots")
            spinner.start()
            try:
                place = geocode(city)
                spinner.stop()

                if not place:
                    console.print(f"[red]❌ City '{city}' not found. Try again.[/red]\n")
                    continue

                df = get_forecast(place["lat"], place["lon"])
                if df is None or df.empty:
                    console.print("[yellow]⚠️ No forecast data available.[/yellow]\n")
                    continue

                try:
                    plot_forecast(df, place["name"])
                except Exception as e:
                    console.print(f"[red]Plot error:[/red] {e}\n")

            except requests.Timeout:
                spinner.stop()
                console.print("[red]⏳ Forecast request timed out. Try again.[/red]")
            except requests.RequestException as e:
                spinner.stop()
                console.print(f"[red]Network error while fetching forecast:[/red] {e}")
            except Exception as e:
                spinner.stop()
                console.print(f"[red]Unexpected error:[/red] {e}")

        # ---------- Option 3: Help ----------
        elif choice == "Help":
            console.print(Panel.fit(
                "[cyan]Usage Tips[/cyan]\n"
                "• Enter a valid city name to fetch live weather data.\n"
                "• Forecast graphs display temperature and humidity trends.\n"
                "• Use [yellow]Ctrl + C[/yellow] anytime to quit safely.\n\n"
                "[green]Data Source:[/green] OpenWeatherMap API",
                title="[bold white]Help Menu[/bold white]",
                box=box.ROUNDED
            ))

        # ---------- Option 4: Exit ----------
        elif choice == "Exit":
            console.print("\n[bold green]Goodbye! Stay weather-wise ☀️[/bold green]\n")
            break

#------Run Program------
if __name__ == "__main__":
    main()