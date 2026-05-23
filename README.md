# AQUA

**A simple, modular AI Agent CLI**

AQUA is a lightweight AI agent framework built in Python. It provides interactive chat, tool execution, persistent memory, and persona management — all through a clean CLI interface.

## Features

- 🤖 **Interactive Chat** — Multi-turn conversation with LLM
- 🎭 **Persona System** — Customizable system prompts and personality
- 🔧 **Tools / Function Calling** — Execute commands, read files, and more
- 💾 **Persistent Memory** — Remember context across sessions
- 📱 **Platform Messaging** — Connect to Telegram and other platforms

## Tech Stack

- Python 3.10+
- openai (LLM API client)
- prompt_toolkit (interactive CLI)
- rich (formatted output)
- pyyaml (config management)

## Quick Start

```bash
git clone https://github.com/galinaplinoel-stack/aqua.git
cd aqua
pip install -r requirements.txt
python main.py
```

## Configuration

Edit `config/config.yaml`:

```yaml
provider:
  base_url: "https://api.openai.com/v1"
  api_key: "your-key-here"
  model: "gpt-4o"

persona:
  name: "AQUA"
  system_prompt: "You are AQUA, a helpful AI assistant."
```

## Architecture

```
aqua/
├── agent/
│   ├── core.py          # Chat loop + LLM interaction
│   ├── tools.py         # Tool registry + execution
│   ├── memory.py        # Persistent memory (JSON)
│   └── persona.py       # System prompt management
├── config/
│   └── config.yaml      # Provider, persona, settings
├── cli.py               # CLI entry point
├── main.py              # Main runner
└── requirements.txt
```

## License

MIT
