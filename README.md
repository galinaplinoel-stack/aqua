# AQUA

**A simple, modular AI Agent CLI with multi-agent hierarchy**

AQUA is a lightweight AI agent framework built in Python. It provides interactive chat, tool execution, persistent memory, persona management, and a multi-agent company hierarchy — all through a clean CLI interface.

## Features

- 🤖 **Interactive Chat** — Multi-turn conversation with LLM
- 🎭 **Persona System** — Customizable via `Aqua.md` file
- 🔧 **Tools / Function Calling** — Execute commands, read files, and more
- 💾 **Persistent Memory** — Remember context across sessions
- 🏢 **Company Hierarchy** — Departments, roles, org chart
- 👥 **Sub-Agents** — Create specialized agents with specific roles
- 📋 **Task Delegation** — Assign and track tasks across agents
- 📱 **Platform Messaging** — Connect to Telegram and other platforms

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
  path: "Aqua.md"

memory:
  enabled: true
  path: "memory.json"

tools:
  enabled: true

hierarchy:
  enabled: true
  path: "hierarchy.json"
```

## Customization

Edit `Aqua.md` to customize AQUA's personality — no code changes needed.

## CLI Commands

### Chat Commands
- `/help` — Show all commands
- `/clear` — Clear conversation history
- `/reload` — Reload persona from `Aqua.md`
- `/history` — Show message count
- `/tools` — List available tools
- `/remember X` — Save a fact to memory
- `/memory` — Show memory stats
- `/search X` — Search memory

### Agent Commands
- `/agents` — List all agents
- `/create NAME ROLE DEPT DESC` — Create new agent
- `/assign TITLE DESC AGENT_ID` — Assign task to agent
- `/tasks [AGENT_ID]` — List delegated tasks
- `/execute TASK_ID` — Execute a delegated task
- `/orgchart` — Show company structure
- `/departments` — List departments

## Multi-Agent System

AQUA can create and manage sub-agents like a company:

```
CEO (AQUA)
├── Engineering
│   ├── CTO
│   ├── Senior Developer
│   └── Developer
├── Product
│   ├── CPO
│   └── Product Manager
└── Operations
    └── COO
```

### Example Usage

```
AQUA> /create Alice "Senior Developer" Engineering "Leads backend development"
Created agent: Alice (senior_developer_a1b2c3d4)

AQUA> /assign "Build API" "Create REST API for user management" senior_developer_a1b2c3d4
Task assigned: task_x1y2z3

AQUA> /execute task_x1y2z3
[Agent executes the task and returns results]
```

Or let AQUA handle it autonomously:

```
AQUA> Create a developer agent and have it write a Python script to fetch weather data
[Creates agent, delegates task, returns results]
```

## Architecture

```
aqua/
├── Aqua.md                    # Persona file (user-editable)
├── agent/
│   ├── core.py                # Chat engine + streaming
│   ├── tools.py               # Tool registry + built-in tools
│   ├── memory.py              # Persistent JSON memory
│   ├── persona.py             # Loads Aqua.md
│   ├── hierarchy.py           # Company structure
│   ├── subagent.py            # Sub-agent system
│   ├── delegation.py          # Task delegation
│   ├── delegation_tools.py    # AI tools for delegation
│   ├── gateway.py             # Multi-platform gateway
│   └── platforms/
│       └── telegram.py        # Telegram bot
├── config/
│   └── config.yaml
├── cli.py
├── main.py
└── requirements.txt
```

## Tech Stack

- Python 3.10+
- openai (LLM API client)
- prompt_toolkit (interactive CLI)
- rich (formatted output)
- pyyaml (config management)
- python-telegram-bot (Telegram integration)

## License

MIT
