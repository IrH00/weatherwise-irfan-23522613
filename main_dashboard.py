# ==========================================================
# Weather Friend Dashboard (CustomTkinter + Matplotlib)
# Modern dark UI - runs standalone in weather_friend folder
# ==========================================================

import threading
import tkinter as tk
import customtkinter as ctk
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'irfan_23522613', 'weather_friend'))


# add current folder to path
sys.path.append(os.path.dirname(__file__))

# ======== Local module imports ========
from weather_data import get_weather_data
from chatbot import talk_to_weather_friend


# ======== Global style config ========
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ======== Matplotlib dark theme ========
def apply_dark_style():
    plt.style.use("default")
    plt.rcParams.update({
        "figure.facecolor": "#15161a",
        "axes.facecolor": "#1a1c20",
        "axes.edgecolor": "#2a2d34",
        "axes.labelcolor": "#dbe2f1",
        "xtick.color": "#cbd5e1",
        "ytick.color": "#cbd5e1",
        "text.color": "#e5e7eb",
        "grid.color": "#2a2d34",
        "axes.grid": True,
        "grid.linestyle": "--",
        "grid.alpha": 0.3,
        "legend.frameon": False
    })

apply_dark_style()


# ======== Async thread helper ========
def run_async(fn, *args):
    threading.Thread(target=fn, args=args, daemon=True).start()


# ==========================================================
#                       MAIN APP
# ==========================================================
class WeatherDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌦️ Weather Friend Dashboard")
        self.geometry("950x600")
        self.minsize(850, 560)

        # ----- State -----
        self._city = "Perth"
        self._days = 3
        self._data = None
        self._series = "Temperature"

        # Layout config
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

    # ======================================================
    # Sidebar
    # ======================================================
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, corner_radius=10)
        sidebar.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        title = ctk.CTkLabel(sidebar, text="☁️ Weather Friend",
                             font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(12, 20))

        ctk.CTkButton(sidebar, text="Current Weather",
                      command=self._show_current, height=36).pack(pady=5, fill="x", padx=10)
        ctk.CTkButton(sidebar, text="5-Day Forecast",
                      command=self._show_forecast, height=36).pack(pady=5, fill="x", padx=10)
        ctk.CTkButton(sidebar, text="Weather Friend (Chat)",
                      command=self._open_chat, height=36).pack(pady=5, fill="x", padx=10)
        ctk.CTkButton(sidebar, text="Help",
                      command=self._show_help, height=36).pack(pady=5, fill="x", padx=10)

        ctk.CTkButton(sidebar, text="Exit", fg_color="#a41717",
                      hover_color="#8f1313", command=self.destroy, height=36).pack(side="bottom", pady=10, padx=10, fill="x")

    # ======================================================
    # Main content area
    # ======================================================
    def _build_main(self):
        self.main = ctk.CTkFrame(self, corner_radius=10)
        self.main.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        self.main.grid_rowconfigure(2, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        header.grid_columnconfigure(0, weight=1)

        self.page_title = ctk.CTkLabel(header, text="Current Weather",
                                       font=ctk.CTkFont(size=22, weight="bold"))
        self.page_title.grid(row=0, column=0, sticky="w")

        self.city_entry = ctk.CTkEntry(header, placeholder_text="Enter city...")
        self.city_entry.insert(0, self._city)
        self.city_entry.grid(row=0, column=1, padx=(10, 8))
        self.city_entry.bind("<Return>", lambda e: self._fetch())

        self.days_menu = ctk.CTkOptionMenu(header, values=["1", "2", "3", "4", "5"],
                                           command=lambda v: self._set_days(v), width=70)
        self.days_menu.set(str(self._days))
        self.days_menu.grid(row=0, column=2, padx=(0, 8))

        ctk.CTkButton(header, text="Fetch", command=self._fetch).grid(row=0, column=3)

        # Cards
        self.cards = {}
        card_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        card_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=6)
        for i, title in enumerate(["Temp (°C)", "Feels", "Humidity", "Wind", "Condition"]):
            frame = ctk.CTkFrame(card_frame, corner_radius=8)
            label_title = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=13))
            label_value = ctk.CTkLabel(frame, text="—", font=ctk.CTkFont(size=20, weight="bold"))
            label_title.pack(anchor="w", padx=8, pady=(6, 0))
            label_value.pack(anchor="w", padx=8, pady=(2, 6))
            frame.grid(row=0, column=i, padx=4, sticky="ew")
            self.cards[title] = label_value
            card_frame.grid_columnconfigure(i, weight=1)

        # Plot frame
        plot_frame = ctk.CTkFrame(self.main, corner_radius=10)
        plot_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(4, 10))
        plot_frame.grid_rowconfigure(1, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        self.series_toggle = ctk.CTkSegmentedButton(plot_frame, values=["Temperature", "Humidity"],
                                                    command=self._update_plot)
        self.series_toggle.set(self._series)
        self.series_toggle.grid(row=0, column=0, sticky="w", padx=8, pady=(6, 0))

        self.fig, self.ax = plt.subplots(figsize=(7, 3.5), dpi=110)
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

    # ======================================================
    # Logic
    # ======================================================
    def _set_days(self, v):
        self._days = int(v)

    def _fetch(self):
        city = self.city_entry.get().strip() or self._city
        self._city = city
        run_async(self._load_data, city)

    def _load_data(self, city):
        try:
            data = get_weather_data(city, forecast_days=self._days)
            self._data = data
            self.after(0, lambda: self._render(data))
        except Exception as e:
            self.after(0, lambda: self._show_popup(f"Error fetching data:\n{e}"))

    def _render(self, data):
        current = data.get("current", {})
        self.cards["Temp (°C)"].configure(text=f"{current.get('temp', '—')}")
        self.cards["Feels"].configure(text=f"{current.get('feels_like', '—')}")
        self.cards["Humidity"].configure(text=f"{current.get('humidity', '—')} %")
        self.cards["Wind"].configure(text=f"{current.get('wind_speed', '—')} m/s")
        self.cards["Condition"].configure(text=current.get("description", "—").title())
        self._update_plot()

    def _update_plot(self, *_):
        if not self._data:
            return
        df = pd.DataFrame(self._data.get("forecast", []))
        if df.empty:
            self.ax.clear()
            self.ax.set_title("No forecast data")
            self.canvas.draw_idle()
            return
        df["time"] = pd.to_datetime(df["time"])
        df = df.sort_values("time")
        df = df.head(self._days * 8)

        self.ax.clear()
        if self.series_toggle.get() == "Temperature":
            self.ax.plot(df["time"], df["temp"], color="#f87171", lw=2.3, marker="o", ms=4)
            self.ax.set_ylabel("°C")
            self.ax.set_title("Temperature Trend")
        else:
            self.ax.plot(df["time"], df["humidity"], color="#60a5fa", lw=2.3, marker="o", ms=4)
            self.ax.fill_between(df["time"], df["humidity"], alpha=0.25, color="#60a5fa")
            self.ax.set_ylabel("%")
            self.ax.set_title("Humidity Trend")
        self.fig.autofmt_xdate(rotation=20)
        self.canvas.draw_idle()

    # ======================================================
    # Other actions
    # ======================================================
    def _show_current(self):
        self.page_title.configure(text="Current Weather")
        self._fetch()

    def _show_forecast(self):
        self.page_title.configure(text="Weather Forecast 📈")
        self._fetch()

    def _open_chat(self):
        chat = ctk.CTkToplevel(self)
        chat.title("Weather Friend Chatbot 🤖")
        chat.geometry("480x360")

        textbox = ctk.CTkTextbox(chat, wrap="word")
        textbox.pack(expand=True, fill="both", padx=8, pady=8)

        entry = ctk.CTkEntry(chat, placeholder_text="Ask Weather Friend...")
        entry.pack(fill="x", padx=8, pady=(0, 8))

        def send_msg(_=None):
            user_q = entry.get().strip()
            if not user_q:
                return
            entry.delete(0, "end")
            textbox.insert("end", f"You: {user_q}\n")
            response = talk_to_weather_friend(user_q)
            textbox.insert("end", f"Weather Friend: {response}\n\n")
            textbox.see("end")

        entry.bind("<Return>", send_msg)
        ctk.CTkButton(chat, text="Send", command=send_msg).pack(pady=(0, 8))

    def _show_help(self):
        self._show_popup("💡 Help:\n- Enter a city name and press Enter or Fetch.\n"
                         "- Use toggle to view Temperature or Humidity.\n"
                         "- Select forecast days (1–5).")

    def _show_popup(self, message):
        popup = ctk.CTkToplevel(self)
        popup.geometry("360x140")
        popup.title("Info")
        ctk.CTkLabel(popup, text=message, wraplength=320).pack(padx=20, pady=20)
        ctk.CTkButton(popup, text="Close", command=popup.destroy).pack(pady=(0, 10))


# ==========================================================
# Run
# ==========================================================
if __name__ == "__main__":
    app = WeatherDashboard()
    app.mainloop()
