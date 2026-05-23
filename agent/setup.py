"""Setup wizard and configuration management."""

import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

console = Console()

CONFIG_PATH = Path("config/config.yaml")

AQUA_BANNER = r"""
[bold cyan]
    █████╗  ██████╗ ██╗   ██╗ █████╗ 
   ██╔══██╗██╔═══██╗██║   ██║██╔══██╗
   ███████║██║   ██║██║   ██║███████║
   ██╔══██║██║▄▄ ██║██║   ██║██╔══██║
   ██║  ██║╚██████╔╝╚██████╔╝██║  ██║
   ╚═╝  ╚═╝ ╚══▀▀═╝  ╚══▀▀═╝ ╚═╝  ╚═╝
[/bold cyan]
[dim]  Enterprise Multi-Agent Framework[/dim]
"""

PROVIDERS = {
    "1": {"name": "OpenAI", "base_url": "https://api.openai.com/v1", "model": "gpt-4o"},
    "2": {"name": "OpenRouter", "base_url": "https://openrouter.ai/api/v1", "model": "openai/gpt-4o"},
    "3": {"name": "Together", "base_url": "https://api.together.xyz/v1", "model": "meta-llama/Llama-3-70b-chat-hf"},
    "4": {"name": "Groq", "base_url": "https://api.groq.com/openai/v1", "model": "llama3-70b-8192"},
    "5": {"name": "Custom", "base_url": "", "model": ""},
    "6": {"name": "MiMo", "base_url": "https://token-plan-sgp.xiaomimimo.com/v1", "model": "mimo-v2.5-pro"},
}


def load_config() -> dict:
    """Load existing config or return default."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}
    return {}


def save_config(config: dict):
    """Save config to file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def setup_wizard():
    """Interactive setup wizard — simple text prompts like Hermes."""
    # Show big banner
    console.print(AQUA_BANNER)

    console.print(Panel(
        "[bold cyan]Setup Wizard[/bold cyan]\n\n"
        "Let's configure AQUA step by step.\n"
        "Press Enter to keep default values.",
        title="🚀 Setup",
        border_style="cyan",
    ))

    config = load_config()

    # === STEP 1: Provider selection (simple numbered list) ===
    console.print("\n[bold]📡 LLM Provider[/bold]")
    console.print("[dim]Supported: OpenAI, OpenRouter, Together, Groq, or any OpenAI-compatible API[/dim]\n")

    console.print("  [cyan]1[/cyan] — OpenAI (api.openai.com)")
    console.print("  [cyan]2[/cyan] — OpenRouter (openrouter.ai)")
    console.print("  [cyan]3[/cyan] — Together (api.together.xyz)")
    console.print("  [cyan]4[/cyan] — Groq (api.groq.com)")
    console.print("  [cyan]5[/cyan] — Custom (enter manually)")
    console.print("  [cyan]6[/cyan] — Xiaomi MiMo (api.mimo.ai)\n")

    provider_choice = Prompt.ask(
        "Select provider",
        default="1",
        choices=["1", "2", "3", "4", "5", "6"],
    )

    selected = PROVIDERS[provider_choice]

    # === STEP 2: API Key ===
    console.print()
    api_key = Prompt.ask("🔑 API Key", password=True)

    if not api_key:
        console.print("[red]API key is required![/red]")
        return

    # === STEP 3: Base URL ===
    if provider_choice == "5":
        base_url = Prompt.ask("Base URL")
    else:
        base_url = Prompt.ask("Base URL", default=selected["base_url"])

    # === STEP 4: Model ===
    if provider_choice == "5":
        model = Prompt.ask("Model name")
    else:
        model = Prompt.ask("Model", default=selected["model"])

    # === Persona configuration ===
    console.print("\n[bold]🎭 Persona[/bold]")
    persona_name = Prompt.ask("Agent name", default="AQUA")
    persona_path = Prompt.ask("Persona file", default="Aqua.md")

    # === Memory configuration ===
    console.print("\n[bold]💾 Memory[/bold]")
    memory_enabled = Confirm.ask("Enable persistent memory?", default=True)
    memory_path = "memory.json"
    if memory_enabled:
        memory_path = Prompt.ask("Memory file", default="memory.json")

    # === Tools configuration ===
    console.print("\n[bold]🔧 Tools[/bold]")
    tools_enabled = Confirm.ask("Enable tools?", default=True)

    # === Hierarchy configuration ===
    console.print("\n[bold]🏢 Multi-Agent[/bold]")
    hierarchy_enabled = Confirm.ask("Enable company hierarchy & sub-agents?", default=True)

    # Build config
    config = {
        "provider": {
            "base_url": base_url,
            "api_key": api_key,
            "model": model,
        },
        "persona": {
            "name": persona_name,
            "path": persona_path,
        },
        "memory": {
            "enabled": memory_enabled,
            "path": memory_path,
        },
        "tools": {
            "enabled": tools_enabled,
            "categories": [],
        },
        "hierarchy": {
            "enabled": hierarchy_enabled,
            "path": "hierarchy.json",
        },
        "agents": {
            "path": "agents",
        },
        "delegation": {
            "path": "delegations.json",
        },
    }

    # Save config
    save_config(config)

    # Secure the file (chmod 600)
    import os
    os.chmod(CONFIG_PATH, 0o600)

    # Show success
    console.print(AQUA_BANNER)
    console.print(Panel(
        f"[green]✓ Configuration saved![/green]\n\n"
        f"Provider : [cyan]{selected['name']}[/cyan]\n"
        f"Base URL : [cyan]{base_url}[/cyan]\n"
        f"Model    : [cyan]{model}[/cyan]\n"
        f"Persona  : [cyan]{persona_name}[/cyan]\n"
        f"Memory   : [cyan]{'✓' if memory_enabled else '✗'}[/cyan]\n"
        f"Tools    : [cyan]{'✓' if tools_enabled else '✗'}[/cyan]\n"
        f"Multi-Agent: [cyan]{'✓' if hierarchy_enabled else '✗'}[/cyan]\n\n"
        f"[dim]Run [bold]python3 main.py[/bold] to start![/dim]",
        title="✅ Setup Complete",
        border_style="green",
    ))


def set_config(key: str, value: str):
    """Set a config value directly."""
    config = load_config()

    keys = key.split(".")
    target = config
    for k in keys[:-1]:
        if k not in target:
            target[k] = {}
        target = target[k]

    if value.lower() in ("true", "yes", "1"):
        value = True
    elif value.lower() in ("false", "no", "0"):
        value = False
    elif value.isdigit():
        value = int(value)

    target[keys[-1]] = value
    save_config(config)

    import os
    os.chmod(CONFIG_PATH, 0o600)

    console.print(f"[green]Set {key} = {value}[/green]")


def show_config():
    """Show current configuration (mask sensitive data)."""
    config = load_config()

    if not config:
        console.print("[yellow]No config found. Run: python3 main.py --setup[/yellow]")
        return

    if "provider" in config and "api_key" in config["provider"]:
        key = config["provider"]["api_key"]
        if len(key) > 8:
            config["provider"]["api_key"] = key[:4] + "..." + key[-4:]

    console.print(AQUA_BANNER)
    console.print(Panel(
        yaml.dump(config, default_flow_style=False, allow_unicode=True),
        title="📋 Configuration",
        border_style="cyan",
    ))


def quick_setup(api_key: str, provider: str = "openai", model: str = ""):
    """Quick setup with just API key."""
    providers = {
        "openai": {"base_url": "https://api.openai.com/v1", "model": "gpt-4o"},
        "openrouter": {"base_url": "https://openrouter.ai/api/v1", "model": "openai/gpt-4o"},
        "together": {"base_url": "https://api.together.xyz/v1", "model": "meta-llama/Llama-3-70b-chat-hf"},
        "groq": {"base_url": "https://api.groq.com/openai/v1", "model": "llama3-70b-8192"},
        "mimo": {"base_url": "https://token-plan-sgp.xiaomimimo.com/v1", "model": "mimo-v2.5-pro"},
    }

    if provider not in providers:
        console.print(f"[red]Unknown provider: {provider}[/red]")
        console.print(f"Available: {', '.join(providers.keys())}")
        return

    p = providers[provider]
    config = {
        "provider": {
            "base_url": p["base_url"],
            "api_key": api_key,
            "model": model or p["model"],
        },
        "persona": {"name": "AQUA", "path": "Aqua.md"},
        "memory": {"enabled": True, "path": "memory.json"},
        "tools": {"enabled": True, "categories": []},
        "hierarchy": {"enabled": True, "path": "hierarchy.json"},
        "agents": {"path": "agents"},
        "delegation": {"path": "delegations.json"},
    }

    save_config(config)

    import os
    os.chmod(CONFIG_PATH, 0o600)

    console.print(AQUA_BANNER)
    console.print(f"[green]✓ Configured with {provider} ({p['model']})[/green]")
    console.print(f"[dim]Run [bold]python3 main.py[/bold] to start![/dim]")


# CLI entry point for config commands
def config_cli():
    """Handle config commands from CLI."""
    args = sys.argv[1:]

    if not args or args[0] == "--setup":
        setup_wizard()
    elif args[0] == "--config":
        if len(args) == 1:
            show_config()
        elif len(args) == 2:
            config = load_config()
            keys = args[1].split(".")
            target = config
            for k in keys:
                if isinstance(target, dict) and k in target:
                    target = target[k]
                else:
                    console.print(f"[red]Key not found: {args[1]}[/red]")
                    return
            console.print(f"{args[1]} = {target}")
        elif len(args) == 3:
            set_config(args[1], args[2])
    elif args[0] == "--quick-setup":
        if len(args) < 2:
            console.print("[red]Usage: python3 main.py --quick-setup API_KEY [provider] [model][/red]")
            return
        api_key = args[1]
        provider = args[2] if len(args) > 2 else "openai"
        model = args[3] if len(args) > 3 else ""
        quick_setup(api_key, provider, model)
    elif args[0] == "--providers":
        console.print(AQUA_BANNER)
        console.print("[bold]Available providers:[/bold]")
        console.print("  [cyan]openai[/cyan]      — OpenAI (GPT-4, GPT-3.5)")
        console.print("  [cyan]openrouter[/cyan] — OpenRouter (multi-model)")
        console.print("  [cyan]together[/cyan]   — Together AI (Llama, Mixtral)")
        console.print("  [cyan]groq[/cyan]       — Groq (fast inference)")
        console.print("  [cyan]mimo[/cyan]       — Xiaomi MiMo")
