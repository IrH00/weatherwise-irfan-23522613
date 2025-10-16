from rich.console import Console

console = Console()

def print_header(title):
    """Prints a consistent styled header panel."""
    console.rule(f"[bold cyan]{title}[/bold cyan]")

def error_message(msg):
    console.print(f"[red]❌ {msg}[/red]")

def success_message(msg):
    console.print(f"[green]✅ {msg}[/green]")
