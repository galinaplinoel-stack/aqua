#!/usr/bin/env python3
"""AQUA - Enterprise Multi-Agent Framework."""

import asyncio
import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel

from agent.memory import Memory
from agent.persona import Persona
from agent.tools import create_registry

console = Console()


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        console.print(f"[red]Config not found: {config_path}[/red]")
        console.print("[yellow]Run: python main.py --setup[/yellow]")
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    """Main entry point."""
    args = sys.argv[1:]

    # Handle config/setup commands
    if not args or args[0] in ("--setup", "--config", "--quick-setup", "--providers"):
        from agent.setup import config_cli
        config_cli()
        return

    # Handle gateway mode
    if "--gateway" in args:
        run_gateway()
        return

    # Default: CLI mode
    from cli import run
    run()


def run_gateway():
    """Run as gateway with platform connections."""
    config = load_config()

    # Setup persona
    persona = Persona(
        name=config["persona"]["name"],
        persona_path=config["persona"]["path"],
    )

    # Setup tools
    tools = None
    if config.get("tools", {}).get("enabled", False):
        tools = create_registry()

    # Setup memory
    memory = None
    memory_config = config.get("memory", {})
    if memory_config.get("enabled", False):
        memory = Memory(
            path=memory_config.get("path", "memory.json"),
            enabled=True,
        )
        memory.increment_sessions()

    # Setup gateway
    from agent.gateway import Gateway
    gateway = Gateway(
        config=config,
        persona=persona,
        tools=tools,
        memory=memory,
    )

    console.print(Panel(
        f"[bold cyan]{persona.name}[/bold cyan] Gateway Mode\n"
        "[dim]Connecting to platforms...[/dim]",
        title="🤖 AQUA Gateway",
        border_style="cyan",
    ))

    # Run gateway
    asyncio.run(gateway.start_platforms())


if __name__ == "__main__":
    main()
