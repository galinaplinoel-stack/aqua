"""CLI interface - interactive terminal experience."""

import sys
from pathlib import Path

import yaml
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.panel import Panel

from agent.core import ChatEngine
from agent.persona import Persona

console = Console()


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        console.print(f"[red]Config not found: {config_path}[/red]")
        console.print("[yellow]Create config/config.yaml first.[/yellow]")
        sys.exit(1)

    with open(path) as f:
        return yaml.safe_load(f)


def run():
    """Main CLI loop."""
    # Load config
    config = load_config()

    # Setup persona
    persona = Persona(
        name=config["persona"]["name"],
        persona_path=config["persona"]["path"],
    )

    # Setup chat engine
    engine = ChatEngine(
        base_url=config["provider"]["base_url"],
        api_key=config["provider"]["api_key"],
        model=config["provider"]["model"],
        persona=persona,
    )

    # Welcome banner
    console.print(Panel(
        f"[bold cyan]{persona.name}[/bold cyan] is ready.\n"
        "[dim]Type your message, /help for commands, or /quit to exit.[/dim]",
        title="🤖 AQUA",
        border_style="cyan",
    ))

    # Setup prompt session with history
    session = PromptSession(
        history=FileHistory(".aqua_history"),
    )

    # Main loop
    while True:
        try:
            user_input = session.prompt(f"\n{persona.name}> ")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input.strip():
            continue

        # Handle commands
        if user_input.startswith("/"):
            cmd = user_input.strip().lower()

            if cmd == "/quit" or cmd == "/exit":
                console.print("[dim]Goodbye![/dim]")
                break

            elif cmd == "/help":
                console.print(Panel(
                    "/help     — Show this help\n"
                    "/clear    — Clear conversation history\n"
                    "/reload   — Reload persona from Aqua.md\n"
                    "/history  — Show message count\n"
                    "/quit     — Exit",
                    title="Commands",
                    border_style="dim",
                ))

            elif cmd == "/clear":
                engine.clear_history()
                console.print("[green]History cleared.[/green]")

            elif cmd == "/reload":
                persona.reload()
                engine.clear_history()
                console.print("[green]Persona reloaded from Aqua.md[/green]")

            elif cmd == "/history":
                count = len(engine.get_history()) - 1  # exclude system
                console.print(f"[dim]{count} messages in history[/dim]")

            else:
                console.print(f"[yellow]Unknown command: {cmd}[/yellow]")

            continue

        # Normal chat
        engine.chat(user_input)
