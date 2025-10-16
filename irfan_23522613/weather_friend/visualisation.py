import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
import pandas as pd


def create_weather_visualisation(weather_data):
    """Show temperature and humidity graphs in one interactive window."""
    df = pd.DataFrame([
        {
            "time": item["dt_txt"],
            "temp": item["main"]["temp"],
            "humidity": item["main"]["humidity"]
        }
        for item in weather_data["list"]
    ])
    df["time"] = pd.to_datetime(df["time"])

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.subplots_adjust(left=0.15)

    # Initial plot: Temperature
    line, = ax.plot(df["time"], df["temp"], color="red", label="Temperature (°C)", linewidth=2)
    ax.set_title("Temperature Trend")
    ax.set_xlabel("Time")
    ax.set_ylabel("°C")
    ax.legend()

    # Add radio buttons for switching
    ax_radio = plt.axes([0.02, 0.4, 0.1, 0.15])  # position: [left, bottom, width, height]
    radio = RadioButtons(ax_radio, ('Temperature', 'Humidity'))

    def update(label):
        ax.clear()
        if label == "Temperature":
            ax.plot(df["time"], df["temp"], color="red", label="Temperature (°C)", linewidth=2)
            ax.set_ylabel("°C")
        else:
            ax.plot(df["time"], df["humidity"], color="blue", label="Humidity (%)", linewidth=2)
            ax.set_ylabel("%")
        ax.set_xlabel("Time")
        ax.set_title(f"{label} Trend")
        ax.legend()
        fig.canvas.draw_idle()

    radio.on_clicked(update)

    plt.show()
