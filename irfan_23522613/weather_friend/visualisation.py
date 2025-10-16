import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def create_temperature_visualisation(weather_data, output_type='figure'):
    """Create a temperature trend line chart."""
    df = pd.DataFrame([
        {"time": item["dt_txt"], "temp": item["main"]["temp"]}
        for item in weather_data["list"]
    ])
    df["time"] = pd.to_datetime(df["time"])

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(df["time"], df["temp"], color="#ff4d4d", linewidth=2)
    ax.set_title("Temperature Trend (°C)", fontsize=12, pad=8)
    ax.set_xlabel("Time", fontsize=10)
    ax.set_ylabel("°C", fontsize=10)
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    return fig


def create_precipitation_visualisation(weather_data, output_type='figure'):
    """Create a humidity trend bar chart."""
    df = pd.DataFrame([
        {"time": item["dt_txt"], "humidity": item["main"]["humidity"]}
        for item in weather_data["list"]
    ])
    df["time"] = pd.to_datetime(df["time"])

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.bar(df["time"], df["humidity"], color="#4da6ff", width=0.04)
    ax.set_title("Humidity Trend (%)", fontsize=12, pad=8)
    ax.set_xlabel("Time", fontsize=10)
    ax.set_ylabel("Humidity (%)", fontsize=10)
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    return fig
