import matplotlib
matplotlib.use("TkAgg")  # must come first
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display


def plot_forecast(df, city):
    """Display a Matplotlib temperature and humidity plot."""
    df = df.copy()
    df["time_str"] = df["time"].dt.strftime("%d/%m %H:%M")

    plt.style.use("seaborn-v0_8-darkgrid")
    plt.figure(figsize=(10, 5))
    plt.plot(df["time_str"], df["temp"], color="red", label="Temperature (°C)")
    plt.plot(df["time_str"], df["humidity"], color="blue", label="Humidity (%)")
    plt.title(f"5-Day Forecast for {city}")
    plt.xlabel("Date/Time")
    plt.ylabel("Values")
    plt.xticks(rotation=45, fontsize=8)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display

def create_temperature_visualisation(weather_data, output_type='display'):
    """Create temperature visualisation from forecast data."""
    df = pd.DataFrame([
        {"time": item["dt_txt"], "temp": item["main"]["temp"]}
        for item in weather_data["list"]
    ])
    df["time"] = pd.to_datetime(df["time"])

    plt.style.use("seaborn-v0_8-darkgrid")
    plt.figure(figsize=(10, 5))
    plt.plot(df["time"], df["temp"], label="Temperature (°C)", color="red", linewidth=2)
    plt.title("Temperature Trend")
    plt.xlabel("Time")
    plt.ylabel("°C")
    plt.legend()
    plt.tight_layout()
    
    if output_type == 'display':
        plt.show()
    else:
        return plt.gcf()

def create_precipitation_visualisation(weather_data, output_type='display'):
    """Create humidity visualisation from forecast data."""
    df = pd.DataFrame([
        {"time": item["dt_txt"], "humidity": item["main"]["humidity"]}
        for item in weather_data["list"]
    ])
    df["time"] = pd.to_datetime(df["time"])

    plt.style.use("seaborn-v0_8-darkgrid")
    plt.figure(figsize=(10, 5))
    plt.bar(df["time"], df["humidity"], color="blue", label="Humidity (%)")
    plt.title("Humidity Over Time")
    plt.xlabel("Time")
    plt.ylabel("%")
    plt.legend()
    plt.tight_layout()
    
    if output_type == 'display':
        plt.show()
    else:
        return plt.gcf()
