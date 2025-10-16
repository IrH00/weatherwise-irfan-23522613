import requests
from rich.console import Console

console = Console()

def fetch_json(url, params=None, headers=None, timeout=10):
    """Generic GET request wrapper with error handling."""
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        console.print("[yellow]⏳ Request timed out. Try again.[/yellow]")
    except requests.exceptions.HTTPError as e:
        console.print(f"[red]HTTP Error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error fetching data: {e}[/red]")
    return None
