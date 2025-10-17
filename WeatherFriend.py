# main_dashboard.py — Weather Friend Dashboard

import os, sys, threading, time
from datetime import datetime

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
from rich.console import Console

# PATH FIX
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# App modules
from irfan_23522613.weather_friend.weather_data import get_weather_data
from irfan_23522613.weather_friend.visualisation import (
    create_temperature_visualisation,
    create_precipitation_visualisation,
)
from irfan_23522613.weather_friend.chatbot import talk_to_weather_friend

console = Console()

# GLOBAL SETTINGS
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

APP_W, APP_H = 1000, 650
PADDING = 10
FONT_TITLE = ("Segoe UI Semibold", 22)
FONT_MD = ("Segoe UI", 14)
FONT_SM = ("Segoe UI", 12)

plt.style.use("seaborn-v0_8-darkgrid")
plt.rcParams.update({
    "axes.facecolor": "#1b1f27",
    "figure.facecolor": "#0d1016",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "text.color": "white"
})


# HELPERS
def run_thread(fn, *args):
    t = threading.Thread(target=fn, args=args, daemon=True)
    t.start()
    return t


def icon_for(desc: str):
    d = (desc or "").lower()
    if "storm" in d: return "⛈️"
    if "rain" in d: return "🌧️"
    if "snow" in d: return "❄️"
    if "cloud" in d: return "☁️"
    if "mist" in d or "fog" in d: return "🌫️"
    return "☀️"


def normalise_forecast_dict(raw):
    """
    Accepts whatever get_weather_data returns and normalises to:
    {"current": {...}, "forecast": [{"time": dt, "temp": x, "humidity": y}, ...], "city": "<name>"}
    """
    if not isinstance(raw, dict):
        return {"error": "Unexpected data format."}

    if "forecast" in raw and isinstance(raw["forecast"], list):
        return raw


    if "list" in raw and isinstance(raw["list"], list):
        out = {"current": raw.get("current", {}), "city": raw.get("city", {}).get("name") or raw.get("name") or ""}
        fc = []
        for item in raw["list"]:
            try:
                fc.append({
                    "time": item.get("dt_txt"),
                    "temp": item.get("main", {}).get("temp"),
                    "humidity": item.get("main", {}).get("humidity"),
                })
            except Exception:
                continue
        out["forecast"] = fc
        return out

    # Fallback to what the app needs:
    if "current" in raw and "hourly" in raw and isinstance(raw["hourly"], list):
        fc = []
        for h in raw["hourly"]:
            fc.append({
                "time": h.get("time") or h.get("dt_txt"),
                "temp": h.get("temp") or h.get("temperature"),
                "humidity": h.get("humidity"),
            })
        return {"current": raw["current"], "forecast": fc, "city": raw.get("city", "")}

    # Give up politely:
    return raw


# CURRENT WEATHER PAGE 
class CurrentWeatherPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=12)
        self.pack_propagate(False)
        ctk.CTkLabel(self, text="Current Weather", font=FONT_TITLE).pack(pady=(8, 6))

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(2, 12))
        self.city_entry = ctk.CTkEntry(
            top, placeholder_text="Search city (e.g., Perth)", height=44,
            font=("Segoe UI", 16), corner_radius=12
        )
        self.city_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.city_entry.bind("<Return>", lambda e: self.fetch())
        ctk.CTkButton(top, text="Fetch", width=120, command=self.fetch).pack(side="left")

        self.card = ctk.CTkFrame(self, corner_radius=16, fg_color="#1a1e27")
        self.card.pack(fill="both", expand=True, padx=20, pady=10)

        self.icon = ctk.CTkLabel(self.card, text="☁️", font=("Segoe UI Emoji", 60))
        self.icon.pack(pady=(20, 10))
        self.city_label = ctk.CTkLabel(self.card, text="—", font=("Segoe UI Semibold", 28))
        self.city_label.pack()
        self.temp_label = ctk.CTkLabel(self.card, text="-- °C", font=("Segoe UI", 44, "bold"))
        self.temp_label.pack(pady=(10, 5))
        self.cond_label = ctk.CTkLabel(self.card, text="Condition: —", font=FONT_MD, wraplength=780, justify="center")
        self.cond_label.pack()
        self.extra_label = ctk.CTkLabel(self.card, text="💧 — %   🌬️ — m/s", font=FONT_MD)
        self.extra_label.pack(pady=(10, 5))
        self.time_label = ctk.CTkLabel(self.card, text="", font=FONT_SM, text_color="#a9b1bc")
        self.time_label.pack()

    def _friendly_error(self, city):
        self.icon.configure(text="🤷")
        self.city_label.configure(text=city.title())
        self.temp_label.configure(text="-- °C")
        self.cond_label.configure(
            text="Couldn't find that city. Please check the spelling and try again."
        )
        self.extra_label.configure(text="💧 — %   🌬️ — m/s")
        self.time_label.configure(text="")

    def fetch(self):
        city = self.city_entry.get().strip()
        if not city:
            return
        self.cond_label.configure(text=f"Fetching weather for {city}…")

        def work():
            try:
                data = get_weather_data(city, days=1)
                if "forecast" not in data or not data["forecast"]:
                    self._friendly_error(city)
                    return

                first = data["forecast"][0]
                desc = "Forecasted conditions"
                self.icon.configure(text=icon_for(desc))
                self.city_label.configure(text=data.get("city", city).title())
                self.temp_label.configure(text=f"{first.get('temp','—')}°C")
                self.cond_label.configure(text=desc)
                self.extra_label.configure(
                    text=f"💧 {first.get('humidity','—')}%   🌬️ — m/s"
                )
                self.time_label.configure(
                    text=datetime.now().strftime("%a, %d %b %Y • %H:%M")
                )
            except Exception:
                console.print_exception()
                self._friendly_error(city)

        run_thread(work)


# FORECAST PAGE
class ForecastPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=12)
        self.pack_propagate(False)
        ctk.CTkLabel(self, text="5-Day Forecast", font=FONT_TITLE).pack(pady=(8, 6))

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(2, 12))
        self.city_entry = ctk.CTkEntry(
            top, placeholder_text="Search city (e.g., Tokyo)", height=44, font=("Segoe UI", 16)
        )
        self.city_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.city_entry.bind("<Return>", lambda e: self.fetch())
        self.days_slider = ctk.CTkSlider(top, from_=1, to=5, number_of_steps=4, width=150)
        self.days_slider.set(5)
        self.days_slider.pack(side="left", padx=(0, 6))
        self.days_label = ctk.CTkLabel(top, text="5 days", width=60, anchor="w")
        self.days_label.pack(side="left", padx=(0, 12))
        self.days_slider.bind(
            "<ButtonRelease-1>",
            lambda e: self.days_label.configure(text=f"{int(self.days_slider.get())} days"),
        )
        ctk.CTkButton(top, text="Generate", width=120, command=self.fetch).pack(side="left", padx=(4, 0))

        # Graph Toggle
        self.toggle = ctk.CTkSegmentedButton(self, values=["Temperature", "Humidity"], command=self.refresh_plot)
        self.toggle.pack(pady=(0, 10))
        self.toggle.set("Temperature")

        # Graph frame
        self.graph_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#161a23")
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = None
        self.cached_data = None

    def _show_msg(self, text):
        for w in self.graph_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.graph_frame, text=text, font=FONT_MD).pack(padx=20, pady=20)

    def refresh_plot(self, *_):
        if not self.cached_data:
            return

        # clear frame
        for w in self.graph_frame.winfo_children():
            w.destroy()

        try:
            # the visualisation module expects the normalised dict
            data = normalise_forecast_dict(self.cached_data)
            if "forecast" not in data or not data["forecast"]:
                self._show_msg("No forecast data to display. Try fetching again.")
                return

            if self.toggle.get() == "Temperature":
                fig = create_temperature_visualisation(data)  # returns a Matplotlib Figure
            else:
                fig = create_precipitation_visualisation(data)

            self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        except Exception:
            console.print_exception()
            self._show_msg("Could not render graph. Please try again.")

    def fetch(self):
        city = self.city_entry.get().strip()
        days = int(self.days_slider.get())
        if not city:
            return

        self._show_msg(f"Loading {days}-day forecast…")

        def work():
            try:
                raw = get_weather_data(city, days)
                if isinstance(raw, dict) and raw.get("error"):
                    self._show_msg("Couldn't find it. Please check spelling.")
                    return

                self.cached_data = raw
                self.refresh_plot()
            except Exception:
                console.print_exception()
                self._show_msg("Couldn't fetch forecast. Check spelling or try again.")

        run_thread(work)


# IMPROVED CHATBOT PAGE
class ChatPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Weather Friend Chat 🤖", font=("Segoe UI Semibold", 22)).pack(pady=(10, 5))

        # Chat display box
        self.chat_frame = ctk.CTkScrollableFrame(self, corner_radius=10, fg_color="#1a1e27")
        self.chat_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.chat_frame._scrollbar.configure(width=12)
        self.chat_frame._parent_canvas.configure(highlightthickness=0, borderwidth=0)

        self.entry_row = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_row.pack(fill="x", padx=20, pady=(0, 20))

        self.entry = ctk.CTkEntry(self.entry_row, placeholder_text="Ask Weather Friend anything…",
                                height=50, font=("Segoe UI", 15))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.send())
        ctk.CTkButton(self.entry_row, text="Send", width=100, command=self.send).pack(side="left")

        # Internal state
        self._animating = False
        self._thinking_label = None

        # Intro message
        self.add_message("Weather Friend", "🌤 Hey there! Ask me about any city’s weather today or in the next 5 days!")

    # UI Message Bubbles
    def add_message(self, sender, text):
        # Colors and alignment
        if sender == "You":
            bubble_color = "#007AFF"   # iMessage blue
            text_color = "white"
            anchor = "e"
            padx = (80, 20)
        else:
            bubble_color = "#2B2E35"   # dark gray bubble for bot
            text_color = "white"
            anchor = "w"
            padx = (20, 80)

        # Create message bubble
        bubble = ctk.CTkFrame(
            self.chat_frame,
            fg_color=bubble_color,
            corner_radius=22,   # iMessage-style rounded edges
        )

        lbl = ctk.CTkLabel(
            bubble,
            text=text,
            wraplength=480,
            justify="left",
            font=("Segoe UI", 14),
            text_color=text_color,
        )
        lbl.pack(padx=12, pady=6)

        bubble.pack(anchor=anchor, padx=padx, pady=6)

        # "Delivered" indicator for user messages
        if sender == "You":
            status = ctk.CTkLabel(
                self.chat_frame,
                text="Delivered",
                text_color="#8E8E93",
                font=("Segoe UI", 10)
            )
            status.pack(anchor="e", padx=(0, 28))

        # Auto-scroll to bottom
        try:
            self.chat_frame._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass


    # Animation
    def start_typing_animation(self):
        self._animating = True
        self._thinking_label = ctk.CTkLabel(self.chat_frame, text="Weather Friend is thinking", font=("Segoe UI", 14))
        self._thinking_label.pack(anchor="w", padx=10, pady=(5, 5))
        try:
            self.chat_frame._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

        def animate():
            dots = 0
            while self._animating:
                dots = (dots + 1) % 4
                if self._thinking_label:
                    self._thinking_label.configure(text=f"Weather Friend is thinking{'.'*dots}")
                time.sleep(0.4)

        run_thread(animate)

    def stop_typing_animation(self):
        self._animating = False
        if self._thinking_label:
            self._thinking_label.destroy()
            self._thinking_label = None

    # Logic
    def send(self):
        user_msg = self.entry.get().strip()
        if not user_msg:
            return
        self.entry.delete(0, "end")
        self.add_message("You", user_msg)
        self.start_typing_animation()
        threading.Thread(target=self.respond, args=(user_msg,), daemon=True).start()

    def respond(self, user_msg):
        try:
            
            try:
                from irfan_23522613.weather_friend.utils import parse_weather_question, generate_weather_response
                parsed = parse_weather_question(user_msg)
            except Exception:
                parsed = {}

            reply = None
            if isinstance(parsed, dict) and parsed.get("location"):
                days = parsed.get("days") or parsed.get("forecast_days") or 1
                raw = get_weather_data(parsed["location"], days=1)
                if isinstance(raw, dict) and raw.get("error"):
                    reply = "Couldn't find that location—check spelling and try again."
                else:
                    reply = generate_weather_response(parsed, normalise_forecast_dict(raw))

            # Fallback to LLM if not a weather question or parsing failed
            if not reply:
                reply = talk_to_weather_friend(user_msg)

        except Exception as e:
            console.print_exception()
            reply = f"⚠️ {e}"

        self.stop_typing_animation()
        self.add_message("Weather Friend", reply)


# MAIN APP
class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Weather Friend")
        self.geometry(f"{APP_W}x{APP_H}")
        self.minsize(850, 560)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        side = ctk.CTkFrame(self, width=260)
        side.grid(row=0, column=0, sticky="nswe")
        ctk.CTkLabel(side, text="🌤 Weather Friend", font=("Segoe UI Semibold", 19)).pack(pady=25)
        ctk.CTkButton(side, text="Current Weather", command=self.show_current).pack(fill="x", padx=12, pady=6)
        ctk.CTkButton(side, text="5-Day Forecast", command=self.show_forecast).pack(fill="x", padx=12, pady=6)
        ctk.CTkButton(side, text="Chatbot 🤖", command=self.show_chat).pack(fill="x", padx=12, pady=6)
        ctk.CTkButton(side, text="Exit", fg_color="#a32020", hover_color="#8d1a1a",
                    command=self.destroy).pack(fill="x", padx=12, pady=(24, 12))

        # Container
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.page_current = CurrentWeatherPage(self.container)
        self.page_forecast = ForecastPage(self.container)
        self.page_chat = ChatPage(self.container)
        for p in (self.page_current, self.page_forecast, self.page_chat):
            p.grid(row=0, column=0, sticky="nswe")

        self.show_current()

    def show_current(self): self.page_current.tkraise()
    def show_forecast(self): self.page_forecast.tkraise()
    def show_chat(self): self.page_chat.tkraise()


if __name__ == "__main__":
    try:
        app = WeatherApp()
        app.protocol("WM_DELETE_WINDOW", app.quit)
        app.mainloop()
    finally:
        print("✅ Weather Friend closed safely.")
        sys.exit(0)
