import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

def create_temperature_visualisation(data):
    """Create temperature line chart from forecast data."""
    if not data or "forecast" not in data or not data["forecast"]:
        raise ValueError("No forecast data to visualize.")
    
    df = pd.DataFrame(data["forecast"])
    
    if "time" not in df.columns:
        if "dt_txt" in df.columns:
            df.rename(columns={"dt_txt": "time"}, inplace=True)
        else:
            raise KeyError("No valid time column found in forecast data.")
    
    
    df["time"] = pd.to_datetime(df["time"])

    fig, ax = plt.subplots(figsize=(8, 4), facecolor="#0d1016")
    ax.plot(df["time"], df["temp"], color="red", linewidth=2.2)
    ax.set_title("Temperature Trend", color="white", fontsize=12, pad=10)
    ax.set_xlabel("Time", color="gray")
    ax.set_ylabel("°C", color="gray")
    ax.tick_params(colors="white", labelsize=8)
    fig.tight_layout()
    return fig



def create_precipitation_visualisation(weather_data):
    """Create humidity bar chart from forecast data."""
    if not weather_data or "forecast" not in weather_data or not weather_data["forecast"]:
        raise ValueError("No forecast data available for plotting humidity.")
    
    df = pd.DataFrame(weather_data["forecast"])
    
    # Ensure correct columns exist
    if "time" not in df.columns:
        # Fallback in case API returned dt_txt
        if "dt_txt" in df.columns:
            df.rename(columns={"dt_txt": "time"}, inplace=True)
        else:
            raise KeyError("No valid time column found in forecast data.")
    
    df["time"] = pd.to_datetime(df["time"])

    fig, ax = plt.subplots(figsize=(8, 4), facecolor="#0d1016")
    ax.bar(df["time"], df["humidity"], color="#3b82f6", alpha=0.8, label="Humidity (%)")
    ax.set_title("Humidity Over Time", color="white", fontsize=12, pad=10)
    ax.set_xlabel("Time", color="gray")
    ax.set_ylabel("Humidity (%)", color="gray")
    ax.tick_params(colors="white", labelsize=8)
    ax.legend(facecolor="#1e1e1e", labelcolor="white")
    fig.tight_layout()
    return fig

