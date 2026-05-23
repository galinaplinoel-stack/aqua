"""CLI interface - interactive terminal experience."""

import sys
from pathlib import Path

import yaml
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.panel import Panel

from agent.core import ChatEngine
from agent.delegation import DelegationManager
from agent.hierarchy import Hierarchy, create_default_hierarchy
from agent.memory import Memory
from agent.persona import Persona
from agent.subagent import AgentFactory
from agent.tools import ToolRegistry, create_default_registry
from agent.delegation_tools import create_delegation_tools

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

    # Setup hierarchy
    hierarchy_config = config.get("hierarchy", {})
    hierarchy_path = hierarchy_config.get("path", "hierarchy.json")
    if hierarchy_config.get("enabled", False):
        hierarchy = create_default_hierarchy(hierarchy_path)
    else:
        hierarchy = Hierarchy(path=hierarchy_path)

    # Setup agent factory
    agent_factory = AgentFactory(
        client=None,  # Will be set after ChatEngine creation
        model=config["provider"]["model"],
        tools=tools,
        memory_path=config.get("agents", {}).get("path", "agents"),
    )

    # Setup delegation manager
    delegation = DelegationManager(
        agent_factory=agent_factory,
        path=config.get("delegation", {}).get("path", "delegations.json"),
    )

    # Setup chat engine
    engine = ChatEngine(
        base_url=config["provider"]["base_url"],
        api_key=config["provider"]["api_key"],
        model=config["provider"]["model"],
        persona=persona,
        tools=tools,
        memory=memory,
    )

    # Set client in agent factory
    agent_factory.client = engine.client

    # Register delegation tools if hierarchy enabled
    if hierarchy_config.get("enabled", False) and tools:
        delegation_tools = create_delegation_tools(agent_factory, hierarchy, delegation)
        for name, tool_data in delegation_tools.items():
            tools.register_dynamic(name, tool_data["func"], tool_data["schema"])
        console.print(f"[dim]Loaded {len(delegation_tools)} delegation tools[/dim]")

    # Welcome banner
    features = []
    if tools:
        features.append(f"{len(tools.tools)} tools")
    if memory:
        features.append("memory")
    if hierarchy_config.get("enabled", False):
        features.append("hierarchy")
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
                help_text = """
[bold]Chat Commands[/bold]
/help        — Show this help
/clear       — Clear conversation history
/reload      — Reload persona from Aqua.md
/history     — Show message count
/tools       — List available tools
/remember X  — Save a fact to memory
/memory      — Show memory stats
/search X    — Search memory
/quit        — Exit

[bold]Agent Commands[/bold]
/agents              — List all agents
/create NAME ROLE DEPT DESC — Create new agent
/assign TITLE DESC AGENT_ID — Assign task
/tasks [AGENT_ID]   — List tasks
/execute TASK_ID     — Execute a task
/orgchart           — Show company structure
/departments        — List departments
"""
                console.print(Panel(help_text, title="Commands", border_style="dim"))

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

            # Agent commands
            elif cmd == "/agents":
                agents = agent_factory.list_agents()
                if not agents:
                    console.print("[dim]No agents created yet. Use /create to add one.[/dim]")
                else:
                    for agent in agents:
                        console.print(f"  [cyan]{agent['id']}[/cyan]: {agent['name']} ({agent['role']} in {agent['department']})")

            elif cmd == "/create":
                if not arg:
                    console.print("[yellow]Usage: /create NAME ROLE DEPT DESCRIPTION[/yellow]")
                else:
                    parts = arg.split(" ", 3)
                    if len(parts) < 4:
                        console.print("[yellow]Usage: /create NAME ROLE DEPT DESCRIPTION[/yellow]")
                    else:
                        name, role, dept, desc = parts
                        try:
                            agent = agent_factory.create_agent(
                                name=name,
                                role=role,
                                department=dept,
                                description=desc,
                            )
                            console.print(f"[green]Created agent: {agent.name} ({agent.agent_id})[/green]")
                        except Exception as e:
                            console.print(f"[red]Error: {e}[/red]")

            elif cmd == "/assign":
                if not arg:
                    console.print("[yellow]Usage: /assign TITLE DESCRIPTION AGENT_ID[/yellow]")
                else:
                    parts = arg.split(" ", 2)
                    if len(parts) < 3:
                        console.print("[yellow]Usage: /assign TITLE DESCRIPTION AGENT_ID[/yellow]")
                    else:
                        title, desc, agent_id = parts
                        try:
                            task = delegation.delegate_task(
                                title=title,
                                description=desc,
                                agent_id=agent_id,
                            )
                            console.print(f"[green]Task assigned: {task.task_id}[/green]")
                        except Exception as e:
                            console.print(f"[red]Error: {e}[/red]")

            elif cmd == "/tasks":
                delegation.display_tasks(arg if arg else None)

            elif cmd == "/execute":
                if not arg:
                    console.print("[yellow]Usage: /execute TASK_ID[/yellow]")
                else:
                    result = delegation.execute_task(arg)
                    console.print(f"[green]Result:[/green]\n{result}")

            elif cmd == "/orgchart":
                hierarchy.display()

            elif cmd == "/departments":
                departments = hierarchy.departments
                if not departments:
                    console.print("[dim]No departments defined[/dim]")
                else:
                    for name, dept in departments.items():
                        console.print(f"  [cyan]{name}[/cyan]: {dept.description}")
                        if dept.head:
                            console.print(f"    Head: {dept.head}")

            else:
                console.print(f"[yellow]Unknown command: {cmd}[/yellow]")

            continue

        # Normal chat
        engine.chat(user_input)
