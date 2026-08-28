import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

ROOT = Path(__file__).resolve().parent


def version_of(command: list[str]) -> str | None:
    if shutil.which(command[0]) is None:
        return None
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
    except Exception:
        return None
    output = (result.stdout + result.stderr).strip()
    return output.splitlines()[0] if output else None


def check_gitignore() -> tuple[bool, str]:
    path = ROOT / ".gitignore"
    if not path.exists():
        return False, "no encontrado"
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    if ".env" in lines:
        return True, "protege .env"
    return False, "existe pero no ignora .env"


def main() -> None:
    python_ok = sys.version_info[:2] == (3, 12)

    checks: list[tuple[str, bool, str, bool]] = [
        ("Python 3.12", python_ok, sys.version.split()[0], True),
    ]

    uv_version = version_of(["uv", "--version"])
    checks.append(("uv", uv_version is not None, uv_version or "no encontrado", True))

    git_version = version_of(["git", "--version"])
    checks.append(("Git", git_version is not None, git_version or "no encontrado", True))

    docker_version = version_of(["docker", "--version"])
    checks.append(
        ("Docker", docker_version is not None, docker_version or "no encontrado", True)
    )

    gitignore_ok, gitignore_detail = check_gitignore()
    checks.append((".gitignore protege .env", gitignore_ok, gitignore_detail, True))

    table = Table(title="Verificación del Entorno — Clase 1")
    table.add_column("Componente", style="bold")
    table.add_column("Estado", justify="center")
    table.add_column("Detalle", style="dim")

    for name, ok, detail, required in checks:
        status = "[green]OK[/green]" if ok else ("[red]FALLÓ[/red]" if required else "[yellow]ADVERTENCIA[/yellow]")
        table.add_row(name, status, detail)

    console.print(table)

    required_ok = all(ok for _, ok, _, required in checks if required)

    if required_ok:
        console.print("\n[bold green]Entorno listo. Nos vemos en la Clase 2.[/bold green]")
    else:
        console.print("\n[bold red]Algunos componentes requeridos fallaron. Corrígelos antes de la Clase 2.[/bold red]")

    sys.exit(0 if required_ok else 1)


if __name__ == "__main__":
    main()
