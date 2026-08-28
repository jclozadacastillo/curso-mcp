import sys
from rich import print
from rich.panel import Panel


def main():
    print(Panel.fit("[bold green]¡Hola![/bold green] Bienvenido al curso de MCP."))
    print(f"[bold cyan]Versión de Python:[/bold cyan] {sys.version}")
    print(f"[bold yellow]sys.executable:[/bold yellow] {sys.executable}")


if __name__ == "__main__":
    main()