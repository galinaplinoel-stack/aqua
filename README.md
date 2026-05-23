# AQUA

**Enterprise-grade Multi-Agent Framework with Organizational Hierarchy**

AQUA is a powerful AI agent framework built in Python that simulates a real company structure. It features interactive chat, tool execution, persistent memory, persona management, and a complete multi-agent hierarchy system where AI agents can create, manage, and delegate tasks to specialized sub-agents — all through a clean CLI interface.

## Why AQUA?

Most AI agent frameworks treat agents as isolated workers. AQUA takes a different approach — it models agents as an organization with departments, roles, reporting lines, and task delegation. This enables:

- **Scalable task decomposition** — Break complex tasks into specialized subtasks
- **Role-based expertise** — Each agent has specific skills and permissions
- **Organizational structure** — Clear hierarchy and responsibility chains
- **Autonomous coordination** — Agents can create and manage other agents

## Features

### Core
- 🤖 **Interactive Chat** — Multi-turn streaming conversation with LLM
- 🎭 **Persona System** — Fully customizable via `Aqua.md` file
- 🔧 **Tools / Function Calling** — Execute commands, read/write files, and more
- 💾 **Persistent Memory** — Remember context and facts across sessions
- 📱 **Platform Messaging** — Connect to Telegram and other platforms

### Multi-Agent System
- 🏢 **Company Hierarchy** — Define departments, roles, and org chart
- 👥 **Sub-Agent Creation** — Spawn specialized agents with specific roles
- 📋 **Task Delegation** — Assign, track, and execute tasks across agents
- 🤖 **Autonomous Operation** — AI can create agents and delegate tasks without manual intervention
- 🔐 **Role-Based Permissions** — Control what each agent can do

## Quick Start

```bash
git clone https://github.com/galinaplinoel-stack/aqua.git
cd aqua
pip install -r requirements.txt

# Configure your API key
nano config/config.yaml

# Run in CLI mode
python main.py

# Or run in gateway mode (Telegram)
python main.py --gateway
```

## Configuration

Edit `config/config.yaml`:

```yaml
# LLM Provider
provider:
  base_url: "https://api.openai.com/v1"
  api_key: "your-key-here"
  model: "gpt-4o"

# Agent Persona
persona:
  name: "AQUA"
  path: "Aqua.md"

# Persistent Memory
memory:
  enabled: true
  path: "memory.json"

# Tool System
tools:
  enabled: true

# Company Hierarchy
hierarchy:
  enabled: true
  path: "hierarchy.json"

# Sub-Agent Storage
agents:
  path: "agents"

# Task Delegation
delegation:
  path: "delegations.json"

# Platform Integrations
platforms:
  # telegram:
  #   token: "your-bot-token"
  #   allowed_chat_ids:
  #     - "your-chat-id"
```

## Customization

### Persona

Edit `Aqua.md` to customize AQUA's personality, tone, rules, and behavior. No code changes needed — just edit and restart.

### Company Structure

Edit `hierarchy.json` to define your organization:

```json
{
  "departments": {
    "Engineering": {
      "description": "Software development and technical operations",
      "head": "CTO",
      "roles": {
        "CTO": {
          "description": "Chief Technology Officer",
          "permissions": ["approve_architecture", "manage_team"],
          "reports_to": "CEO"
        }
      }
    }
  }
}
```

Or use the default structure and modify it via CLI commands.

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
- `/quit` — Exit

### Agent Management
- `/agents` — List all agents with their roles and status
- `/create NAME ROLE DEPT DESC` — Create a new agent
- `/assign TITLE DESC AGENT_ID` — Assign a task to an agent
- `/tasks [AGENT_ID]` — List delegated tasks (optionally filtered by agent)
- `/execute TASK_ID` — Execute a delegated task

### Organization
- `/orgchart` — Display full company structure
- `/departments` — List all departments and their roles

## Multi-Agent System

### Default Company Structure

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

### Manual Usage

```bash
# Create an agent
AQUA> /create Alice "Senior Developer" Engineering "Leads backend development"
Created agent: Alice (senior_developer_a1b2c3d4)

# Assign a task
AQUA> /assign "Build REST API" "Create user management API with FastAPI" senior_developer_a1b2c3d4
Task assigned: task_x1y2z3

# Execute the task
AQUA> /execute task_x1y2z3
[Agent executes and returns results]

# View org chart
AQUA> /orgchart
```

### Autonomous Usage

AQUA can handle everything automatically:

```
AQUA> Create a developer agent and have it write a Python script to fetch weather data
[Creates agent, delegates task, returns results]

AQUA> Set up a product team and have them design a new feature spec
[Creates CPO + Product Manager, coordinates task]
```

The AI uses tools to:
1. Create agents with appropriate roles
2. Delegate tasks based on expertise
3. Execute and coordinate work
4. Return consolidated results

## Architecture

```
aqua/
├── Aqua.md                    # Persona file (user-editable)
├── agent/
│   ├── core.py                # Chat engine + streaming + tool execution
│   ├── tools.py               # Tool registry + built-in tools
│   ├── memory.py              # Persistent JSON memory with search
│   ├── persona.py             # Loads Aqua.md as system prompt
│   ├── hierarchy.py           # Company structure (departments, roles)
│   ├── subagent.py            # Sub-agent factory + role-based agents
│   ├── delegation.py          # Task delegation + tracking
│   ├── delegation_tools.py    # AI tools for autonomous agent management
│   ├── gateway.py             # Multi-platform session manager
│   └── platforms/
│       ├── __init__.py        # Base Platform interface
│       └── telegram.py        # Telegram bot integration
├── config/
│   └── config.yaml            # All configuration
├── docs/
│   └── specs/                 # Design specifications
├── cli.py                     # Interactive CLI with all commands
├── main.py                    # Entry point (--gateway for platform mode)
└── requirements.txt
```

## Tech Stack

- **Python 3.10+**
- **openai** — LLM API client (OpenAI-compatible)
- **prompt_toolkit** — Interactive CLI with history
- **rich** — Formatted terminal output
- **pyyaml** — Configuration management
- **python-telegram-bot** — Telegram integration

## Use Cases

- **Software Development Teams** — Create dev, QA, and ops agents
- **Product Management** — Product manager + designer agents
- **Content Creation** — Writer + editor + reviewer agents
- **Research** — Researcher + analyst + summarizer agents
- **Customer Support** — Triage + specialist + escalation agents

## License

MIT
