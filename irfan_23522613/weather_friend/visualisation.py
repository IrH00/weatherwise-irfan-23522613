import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# ========= Aesthetic Configuration =========
def set_dark_theme(ax, title):
    """Apply a sleek dark theme to Matplotlib axes."""
    ax.set_facecolor("#1E1E1E")
    ax.figure.set_facecolor("#121212")

    ax.tick_params(axis="x", colors="white", labelsize=9)
    ax.tick_params(axis="y", colors="white", labelsize=9)
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("#00BFFF")

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.grid(True, color="#2E2E2E", linestyle="--", alpha=0.4)
    ax.set_title(title, fontsize=13, pad=10, weight="bold")


# ========= Temperature Chart =========
def create_temperature_visualisation(weather_data, output_type="figure"):
    """Modern smooth temperature trend."""
    df = pd.DataFrame([
        {"time": item["dt_txt"], "temp": item["main"]["temp"]}
        for item in weather_data["list"]
    ])
    df["time"] = pd.to_datetime(df["time"])
    df = df.groupby("time").mean().reset_index()

    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    set_dark_theme(ax, "🌡️ Temperature Trend (°C)")

    # smooth line
    x = np.arange(len(df))
    y = df["temp"].values
    ax.plot(df["time"], y, color="#FF5F5F", linewidth=2.5, marker="o",
            markerfacecolor="#ff8c8c", markersize=4, alpha=0.9)

    # gradient fill
    ax.fill_between(df["time"], y, color="#ff5f5f", alpha=0.1)

    ax.set_xlabel("Time")
    ax.set_ylabel("°C")
    fig.tight_layout(pad=2)
    return fig


# ========= Humidity Chart =========
def create_precipitation_visualisation(weather_data, output_type="figure"):
    """Modern bar chart for humidity."""
    df = pd.DataFrame([
        {"time": item["dt_txt"], "humidity": item["main"]["humidity"]}
        for item in weather_data["list"]
    ])
    df["time"] = pd.to_datetime(df["time"])
    df = df.groupby("time").mean().reset_index()

    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    set_dark_theme(ax, "💧 Humidity Trend (%)")

    # gradient bars
    bars = ax.bar(df["time"], df["humidity"], color="#00BFFF", width=0.03, alpha=0.9)
    for bar in bars:
        bar.set_edgecolor("#1E90FF")
        bar.set_linewidth(0.5)
        bar.set_alpha(0.8)

    ax.set_xlabel("Time")
    ax.set_ylabel("Humidity (%)")
    fig.tight_layout(pad=2)
    return fig
