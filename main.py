import threading
import tkinter as tk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from rich.console import Console

from irfan_23522613.weather_friend.weather_data import get_weather_data
from irfan_23522613.weather_friend.visualisation import (
    create_temperature_visualisation,
    create_precipitation_visualisation
)
from irfan_23522613.weather_friend.chatbot import talk_to_weather_friend


# ========== Setup ==========
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

WINDOW_W, WINDOW_H = 900, 550
console = Console()


def threadify(fn):
    """Run function in a separate thread (to keep UI responsive)."""
    t = threading.Thread(target=fn, daemon=True)
    t.start()
    return t


# ========== Main App ==========
class WeatherApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("🌦️ Weather Friend")
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.minsize(750, 500)

        # Left navigation panel
        self.sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="🌤 Weather Friend",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))

        self._add_nav_button("Current Weather", self.build_current_page)
        self._add_nav_button("5-Day Forecast", self.build_forecast_page)
        self._add_nav_button("Weather Friend (Chat)", self.build_chat_page)
        self._add_nav_button("Help", self.build_help_page)

        ctk.CTkButton(self.sidebar, text="Exit", fg_color="#b22222",
                      hover_color="#7f1d1d", command=self.destroy).pack(side="bottom", pady=20)

        # Main content area
        self.content = ctk.CTkFrame(self)
        self.content.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.canvas = None
        self.weather_cache = None
        self.current_page = None

        self.build_current_page()

    # ========== Sidebar Helper ==========
    def _add_nav_button(self, text, command):
        ctk.CTkButton(self.sidebar, text=text, width=160, command=command).pack(pady=5)

    # ========== Page Builders ==========
    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # ===== Page 1: Current Weather =====
    def build_current_page(self):
        self._clear_content()
        self.current_page = "current"

        title = ctk.CTkLabel(self.content, text="Current Weather",
                             font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(5, 10))

        # Input row
        input_row = ctk.CTkFrame(self.content)
        input_row.pack(pady=10, fill="x")

        self.city_current = ctk.CTkEntry(input_row, placeholder_text="Enter city name...")
        self.city_current.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.city_current.bind("<Return>", lambda e: self._fetch_current_weather())

        ctk.CTkButton(input_row, text="Fetch", width=100,
                      command=self._fetch_current_weather).pack(side="right")

        self.output_current = ctk.CTkTextbox(self.content, wrap="word", height=280)
        self.output_current.pack(fill="both", expand=True, pady=10)
        self.output_current.insert("end", "Type a city and press [Enter] or Fetch.\n")

    def _fetch_current_weather(self):
        city = self.city_current.get().strip()
        if not city:
            return
        self.output_current.delete("1.0", "end")
        self.output_current.insert("end", f"Fetching current weather for {city}...\n")

        def task():
            try:
                data = get_weather_data(city, forecast_days=1)
                current = data.get("current") or data["list"][0]["main"]
                desc = data["list"][0]["weather"][0]["description"].title()
                text = (
                    f"\nCity: {city.title()}\n"
                    f"Temperature: {current['temp']} °C\n"
                    f"Feels like: {current.get('feels_like', '–')} °C\n"
                    f"Humidity: {current['humidity']} %\n"
                    f"Condition: {desc}\n"
                )
                self.output_current.insert("end", text)
            except Exception as e:
                self.output_current.insert("end", f"\n[Error] {e}")

        threadify(task)

    # ===== Page 2: 5-Day Forecast =====
    def build_forecast_page(self):
        self._clear_content()
        self.current_page = "forecast"

        title = ctk.CTkLabel(self.content, text="Weather Forecast 📊",
                             font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(5, 10))

        ctrl = ctk.CTkFrame(self.content)
        ctrl.pack(pady=10, fill="x")

        self.city_forecast = ctk.CTkEntry(ctrl, placeholder_text="Enter city name...")
        self.city_forecast.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.city_forecast.bind("<Return>", lambda e: self._fetch_and_plot_forecast())

        self.days_var = tk.StringVar(value="3")
        ctk.CTkOptionMenu(ctrl, variable=self.days_var,
                          values=["1", "2", "3", "4", "5"], width=80).pack(side="left", padx=(0, 10))

        ctk.CTkButton(ctrl, text="Generate", width=100,
                      command=self._fetch_and_plot_forecast).pack(side="right")

        self.plot_holder = ctk.CTkFrame(self.content)
        self.plot_holder.pack(fill="both", expand=True, pady=(10, 0))

        self.toggle_var = ctk.StringVar(value="Temperature")
        ctk.CTkSegmentedButton(self.content, values=["Temperature", "Humidity"],
                               variable=self.toggle_var,
                               command=self._refresh_plot_if_cached).pack(pady=10)

    def _fetch_and_plot_forecast(self):
        city = self.city_forecast.get().strip()
        if not city:
            return
        days = int(self.days_var.get())
        self.weather_cache = None

        def task():
            try:
                data = get_weather_data(city, forecast_days=days)
                self.weather_cache = data
                self._refresh_plot_if_cached()
            except Exception as e:
                console.print(f"[red]Error generating forecast:[/red] {e}")

        threadify(task)

    def _refresh_plot_if_cached(self, *args):
        if not self.weather_cache:
            return
        mode = self.toggle_var.get()
        fig = (create_temperature_visualisation(self.weather_cache)
               if mode == "Temperature"
               else create_precipitation_visualisation(self.weather_cache))
        self._embed_figure(fig)

    def _embed_figure(self, fig):
        if hasattr(self, "canvas") and self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_holder)
        self.canvas.draw()
        widget = self.canvas.get_tk_widget()
        widget.pack(fill="both", expand=True, padx=15, pady=10)
        widget.configure(bg="#151515", highlightthickness=0)

    # ===== Page 3: Chatbot =====
    def build_chat_page(self):
        self._clear_content()
        self.current_page = "chat"

        ctk.CTkLabel(self.content, text="🤖 Talk to Weather Friend!",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.chat_display = ctk.CTkTextbox(self.content, wrap="word", height=300)
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)
        self.chat_display.insert("end", "Weather Friend is ready! Type your question below.\n\n")

        entry_row = ctk.CTkFrame(self.content)
        entry_row.pack(fill="x", padx=10, pady=(0, 10))

        self.chat_input = ctk.CTkEntry(entry_row, placeholder_text="Ask about weather or type 'exit'...")
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.chat_input.bind("<Return>", lambda e: self._send_message())

        ctk.CTkButton(entry_row, text="Send", width=80, command=self._send_message).pack(side="right")

    def _send_message(self):
        user_msg = self.chat_input.get().strip()
        if not user_msg:
            return
        self.chat_display.insert("end", f"You: {user_msg}\n")
        self.chat_input.delete(0, "end")
        if user_msg.lower() in ["exit", "quit"]:
            self.chat_display.insert("end", "👋 Goodbye from Weather Friend!\n")
            return

        def task():
            try:
                reply = talk_to_weather_friend(user_msg)
                self.chat_display.insert("end", f"Weather Friend: {reply}\n\n")
            except Exception as e:
                self.chat_display.insert("end", f"[Error] {e}\n")

        threadify(task)

    # ===== Page 4: Help =====
    def build_help_page(self):
        self._clear_content()
        help_text = (
            "💡 [b]Weather Friend Help[/b]\n\n"
            "• [1] Current Weather — get live weather for any city.\n"
            "• [2] Forecast — 1–5 day graphs for temperature/humidity.\n"
            "• [3] Chat — talk naturally to Weather Friend.\n"
            "• Press [Enter] in city box to fetch quickly.\n"
            "• Type 'exit' in chat to leave.\n"
        )
        ctk.CTkLabel(self.content, text=help_text, justify="left",
                     font=ctk.CTkFont(size=14)).pack(padx=20, pady=20)


# ========== Run ==========
if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
