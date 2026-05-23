"""CLI interface - interactive terminal experience."""

import sys
from pathlib import Path

import yaml
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.panel import Panel

from agent.core import ChatEngine
from agent.memory import Memory
from agent.persona import Persona
from agent.tools import ToolRegistry, create_default_registry

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

    # Setup tools
    tools = None
    if config.get("tools", {}).get("enabled", False):
        tools = create_default_registry()
        console.print(f"[dim]Loaded {len(tools.tools)} tools[/dim]")

    # Setup memory
    memory = None
    memory_config = config.get("memory", {})
    if memory_config.get("enabled", False):
        memory = Memory(
            path=memory_config.get("path", "memory.json"),
            enabled=True,
        )
        memory.increment_sessions()
        stats = memory.get_stats()
        console.print(f"[dim]Memory: {stats['facts']} facts, {stats['conversations']} conversations[/dim]")

    # Setup chat engine
    engine = ChatEngine(
        base_url=config["provider"]["base_url"],
        api_key=config["provider"]["api_key"],
        model=config["provider"]["model"],
        persona=persona,
        tools=tools,
        memory=memory,
    )

    # Welcome banner
    features = []
    if tools:
        features.append(f"{len(tools.tools)} tools")
    if memory:
        features.append("memory")
    feature_info = f" ({', '.join(features)})" if features else ""

    console.print(Panel(
        f"[bold cyan]{persona.name}[/bold cyan] is ready{feature_info}.\n"
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
            parts = user_input.strip().split(" ", 1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "/quit" or cmd == "/exit":
                # Save conversation summary before exit
                if memory:
                    engine.summarize_and_save()
                console.print("[dim]Goodbye![/dim]")
                break

            elif cmd == "/help":
                console.print(Panel(
                    "/help        — Show this help\n"
                    "/clear       — Clear conversation history\n"
                    "/reload      — Reload persona from Aqua.md\n"
                    "/history     — Show message count\n"
                    "/tools       — List available tools\n"
                    "/remember X  — Save a fact to memory\n"
                    "/memory      — Show memory stats\n"
                    "/search X    — Search memory\n"
                    "/quit        — Exit",
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
                count = len(engine.get_history()) - 1
                console.print(f"[dim]{count} messages in history[/dim]")

            elif cmd == "/tools":
                if tools:
                    for name, tool in tools.tools.items():
                        console.print(f"  [cyan]{name}[/cyan]: {tool.description}")
                else:
                    console.print("[dim]No tools loaded. Enable in config.yaml[/dim]")

            elif cmd == "/remember":
                if not memory:
                    console.print("[yellow]Memory not enabled[/yellow]")
                elif not arg:
                    console.print("[yellow]Usage: /remember <fact>[/yellow]")
                else:
                    memory.add_fact(arg)
                    console.print(f"[green]Remembered: {arg}[/green]")

            elif cmd == "/memory":
                if not memory:
                    console.print("[yellow]Memory not enabled[/yellow]")
                else:
                    stats = memory.get_stats()
                    console.print(Panel(
                        f"Facts: {stats['facts']}\n"
                        f"Conversations: {stats['conversations']}\n"
                        f"Sessions: {stats['sessions']}\n"
                        f"Created: {stats['created']}",
                        title="Memory Stats",
                        border_style="dim",
                    ))

            elif cmd == "/search":
                if not memory:
                    console.print("[yellow]Memory not enabled[/yellow]")
                elif not arg:
                    console.print("[yellow]Usage: /search <query>[/yellow]")
                else:
                    results = memory.search(arg)
                    if results:
                        for r in results:
                            console.print(f"  [{r['type']}] {r['content']}")
                    else:
                        console.print("[dim]No results found[/dim]")

            else:
                console.print(f"[yellow]Unknown command: {cmd}[/yellow]")

            continue

        # Normal chat
        engine.chat(user_input)
