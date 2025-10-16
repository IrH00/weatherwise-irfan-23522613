# ====== Imports ======
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box

from irfan_23522613.weather_friend.weather_data import get_weather_data
from irfan_23522613.weather_friend.visualisation import create_weather_visualisation
from irfan_23522613.weather_friend.chatbot import talk_to_weather_friend


# ====== Console Setup ======
console = Console()


# ====== Main Program ======
def main():
    console.print(Panel.fit("🌦️ [bold cyan]Weather Friend[/bold cyan] 🌦️", box=box.DOUBLE))
    console.print("[green]Welcome to your smart weather assistant![/green]\n")

    while True:
        console.print(Panel.fit(
            "[bold white]1️⃣[/bold white]  Get current weather\n"
            "[bold white]2️⃣[/bold white]  Get weather forecast (1–5 days)\n"
            "[bold white]3️⃣[/bold white]  Talk to Weather Friend 🤖\n"
            "[bold white]4️⃣[/bold white]  Help\n"
            "[bold white]5️⃣[/bold white]  Exit",
            title="[cyan]Main Menu[/cyan]",
            box=box.ROUNDED,
        ))

        choice = Prompt.ask("\n[bold yellow]Select an option (1–5)[/bold yellow]")

        # ===== Option 1: Current Weather =====
        if choice == "1":
            city = Prompt.ask("[bold white]Enter city name[/bold white]")
            console.print(f"[cyan]Fetching current weather for {city}...[/cyan]\n")
            try:
                data = get_weather_data(city, forecast_days=1)
                current = data["list"][0]["main"]
                desc = data["list"][0]["weather"][0]["description"].title()
                console.print(Panel.fit(
                    f"[bold white]{city.title()}[/bold white]\n"
                    f"🌡️ Temperature: [bold cyan]{current['temp']}°C[/bold cyan]\n"
                    f"💧 Humidity: {current['humidity']}%\n"
                    f"☁️ Condition: {desc}",
                    title="[green]Current Weather[/green]",
                    box=box.ROUNDED
                ))
            except Exception as e:
                console.print(f"[red]Error fetching current weather: {e}[/red]\n")

        # ===== Option 2: Forecast =====
        elif choice == "2":
            city = Prompt.ask("[bold white]Enter city name[/bold white]")
            days = int(Prompt.ask("[bold white]Enter forecast days (1–5)[/bold white]", default="3"))
            console.print(f"[cyan]Fetching {days}-day forecast for {city}...[/cyan]\n")

            try:
                data = get_weather_data(city, forecast_days=days)
                create_weather_visualisation(data)
                console.print("[green]✅ Forecast visualisation ready![/green]\n")
            except Exception as e:
                console.print(f"[red]Error generating forecast: {e}[/red]\n")

        # ===== Option 3: Chatbot =====
        elif choice == "3":
            console.print("\n🤖 [bold cyan]Talk to Weather Friend![/bold cyan]")
            while True:
                user_message = Prompt.ask("[bold white]You[/bold white]")
                if user_message.lower() in ["exit", "quit", "bye"]:
                    console.print("[green]👋 Goodbye from Weather Friend![/green]\n")
                    break
                reply = talk_to_weather_friend(user_message)
                console.print(f"[bold magenta]Weather Friend:[/bold magenta] {reply}\n")

        # ===== Option 4: Help =====
        elif choice == "4":
            console.print(Panel.fit(
                "[bold cyan]Usage Guide[/bold cyan]\n\n"
                "1️⃣  Get live current weather for any city\n"
                "2️⃣  View 1–5 day forecast with interactive graphs\n"
                "3️⃣  Chat with Weather Friend (AI bot)\n"
                "4️⃣  Read help info\n"
                "5️⃣  Exit program\n\n"
                "💡 Tip: Type 'exit' anytime in chat to quit safely.",
                title="[white]Help Menu[/white]",
                box=box.ROUNDED
            ))

        # ===== Option 5: Exit =====
        elif choice == "5":
            console.print("\n[bold green]Goodbye! Stay weather-wise ☀️[/bold green]\n")
            break

        else:
            console.print("[red]Invalid choice. Please select between 1–5.[/red]\n")


# ====== Entry Point ======
if __name__ == "__main__":
    main()
