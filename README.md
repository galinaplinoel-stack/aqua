# AQUA

**Enterprise-grade Multi-Agent Framework with Full VPS Management**

AQUA is a powerful AI agent framework built in Python that simulates a real company structure. It features interactive chat, **80+ built-in tools**, persistent memory, persona management, and a complete multi-agent hierarchy system where AI agents can create, manage, and delegate tasks to specialized sub-agents — all through a clean CLI interface.

## Why AQUA?

Most AI agent frameworks treat agents as isolated workers. AQUA takes a different approach — it models agents as an organization with departments, roles, reporting lines, and task delegation. This enables:

- **Scalable task decomposition** — Break complex tasks into specialized subtasks
- **Role-based expertise** — Each agent has specific skills and permissions
- **Organizational structure** — Clear hierarchy and responsibility chains
- **Autonomous coordination** — Agents can create and manage other agents
- **Full system access** — Manage VPS, databases, APIs, and more

## Features

### Core
- 🤖 **Interactive Chat** — Multi-turn streaming conversation with LLM
- 🎭 **Persona System** — Fully customizable via `Aqua.md` file
- 🔧 **80+ Built-in Tools** — Comprehensive tool suite across 16 categories
- 💾 **Persistent Memory** — Remember context and facts across sessions
- 📱 **Platform Messaging** — Connect to Telegram and other platforms

### Multi-Agent System
- 🏢 **Company Hierarchy** — Define departments, roles, and org chart
- 👥 **Sub-Agent Creation** — Spawn specialized agents with specific roles
- 📋 **Task Delegation** — Assign, track, and execute tasks across agents
- 🤖 **Autonomous Operation** — AI can create agents and delegate tasks without manual intervention
- 🔐 **Role-Based Permissions** — Control what each agent can do

## Tool Categories (80+ Tools)

### 🌐 Web & Scraping
- `web_search` — Search the web (DuckDuckGo)
- `scrape_webpage` — Extract content from websites
- `extract_links` — Get all links from a page
- `get_page_metadata` — Extract page metadata

### 🔌 HTTP & API
- `http_request` — Full HTTP client (GET, POST, PUT, DELETE)
- `api_get`, `api_post`, `api_put`, `api_delete` — Simple API calls
- `download_file` — Download files from URLs

### 💻 Code Execution
- `run_python` — Execute Python code
- `run_shell` — Run shell commands (full access)
- `run_script` — Execute script files (Python, Bash, Node.js)

### 📁 Git Integration
- `git_clone`, `git_status`, `git_log` — Repository management
- `git_commit`, `git_push`, `git_pull` — Version control

### 🗄️ Database
- `sqlite_query`, `sqlite_create_table`, `sqlite_insert` — SQLite operations
- `postgres_query` — PostgreSQL queries

### 📄 File Formats
- `read_json`, `write_json` — JSON files
- `read_csv` — CSV files
- `read_pdf` — PDF text extraction
- `read_excel` — Excel spreadsheets

### 📧 Email
- `send_email` — Send via SMTP
- `read_emails` — Read via IMAP

### 🖥️ VPS Management (Full Access)
- `system_info` — System information (OS, CPU, memory, disk)
- `process_list` — List running processes
- `service_manage` — Manage systemd services
- `firewall_manage` — UFW firewall rules
- `user_manage` — System user management
- `cron_manage` — Cron job management
- `network_info` — Network interfaces and ports
- `install_package` — Package installation (apt, yum, pip, npm)
- `docker_manage` — Docker container management

### 📊 Monitoring
- `health_check` — Comprehensive system health check
- `disk_usage`, `memory_usage` — Resource monitoring
- `top_processes` — Top processes by CPU/memory
- `check_port` — Port availability check

### 💾 Caching
- `cache_get`, `cache_set`, `cache_clear` — File-based cache
- `rate_limit_check` — Rate limiting

### ⚙️ Workflow
- `create_workflow`, `list_workflows`, `get_workflow` — Workflow engine

### 🔔 Notifications
- `send_discord_webhook` — Discord notifications
- `send_slack_webhook` — Slack notifications
- `send_telegram_message` — Telegram messages
- `send_ntfy` — Push notifications (ntfy.sh)

### 📅 Calendar
- `add_calendar_event`, `list_calendar_events`, `delete_calendar_event`

### 🔌 Plugins
- `load_plugin`, `list_plugins` — Custom tool plugins

### 🔐 Authentication
- `set_credential`, `get_credential`, `list_credentials` — Secure credential storage

### 🧠 Vector Memory
- `add_memory`, `search_memory`, `list_memories` — Semantic memory search

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
  categories: []  # Empty = load all, or specify: ["web", "vps", "git"]

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
```

## Customization

### Persona

Edit `Aqua.md` to customize AQUA's personality, tone, rules, and behavior. No code changes needed — just edit and restart.

### Tool Categories

Load only specific tool categories to reduce token usage:

```yaml
tools:
  enabled: true
  categories: ["web", "vps", "git", "monitoring"]
```

### Custom Plugins

Create custom tools in the `plugins/` directory:

```python
# plugins/my_tool.py
def my_function(param: str) -> str:
    return f"Result: {param}"

TOOLS = {
    "my_tool": {
        "func": my_function,
        "schema": {
            "type": "function",
            "function": {
                "name": "my_tool",
                "description": "My custom tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param": {"type": "string", "description": "Input parameter"}
                    },
                    "required": ["param"]
                }
            }
        }
    }
}
```

## CLI Commands

### Chat Commands
- `/help` — Show all commands
- `/clear` — Clear conversation history
- `/reload` — Reload persona from `Aqua.md`
- `/history` — Show message count
- `/tools [category]` — List tools (optionally by category)
- `/remember X` — Save a fact to memory
- `/memory` — Show memory stats
- `/search X` — Search memory
- `/quit` — Exit

### Agent Management
- `/agents` — List all agents with their roles and status
- `/create NAME ROLE DEPT DESC` — Create a new agent
- `/assign TITLE DESC AGENT_ID` — Assign a task to an agent
- `/tasks [AGENT_ID]` — List delegated tasks
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
```

### Autonomous Usage

AQUA can handle everything automatically:

```
AQUA> Check system health and report any issues
[Runs health_check, reports results]

AQUA> Search the web for latest Python news and summarize
[Uses web_search, summarizes results]

AQUA> Create a developer agent and have it write a weather API
[Creates agent, delegates task, returns results]

AQUA> Check disk usage, clean up temp files, and send report to Discord
[Uses monitoring, shell, notifications tools]
```

## Architecture

```
aqua/
├── Aqua.md                    # Persona file (user-editable)
├── agent/
│   ├── core.py                # Chat engine + streaming + tool execution
│   ├── tools.py               # Tool registry
│   ├── tools/                 # Tool implementations
│   │   ├── __init__.py        # Tool categories
│   │   ├── web.py             # Web search & scraping
│   │   ├── http.py            # HTTP client
│   │   ├── code_exec.py       # Code execution
│   │   ├── git.py             # Git integration
│   │   ├── database.py        # SQLite & PostgreSQL
│   │   ├── file_formats.py    # PDF, CSV, Excel, JSON
│   │   ├── email.py           # SMTP & IMAP
│   │   ├── vps.py             # VPS management
│   │   ├── monitoring.py      # Health checks
│   │   ├── caching.py         # Cache & rate limiting
│   │   ├── workflow.py        # Workflow engine
│   │   ├── notifications.py   # Discord, Slack, Telegram
│   │   ├── calendar.py        # Calendar & scheduling
│   │   ├── plugins.py         # Custom plugins
│   │   ├── auth.py            # Credential management
│   │   └── vector_memory.py   # Semantic memory
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
│   └── config.yaml            # All configuration
├── docs/
│   └── specs/                 # Design specifications
├── cli.py                     # Interactive CLI
├── main.py                    # Entry point
└── requirements.txt
```

## Tech Stack

- **Python 3.10+**
- **openai** — LLM API client (OpenAI-compatible)
- **prompt_toolkit** — Interactive CLI with history
- **rich** — Formatted terminal output
- **pyyaml** — Configuration management
- **requests** — HTTP client
- **beautifulsoup4** — Web scraping
- **PyMuPDF** — PDF processing
- **pandas** — Data processing (CSV, Excel)
- **psycopg2-binary** — PostgreSQL support
- **python-telegram-bot** — Telegram integration

## Use Cases

### System Administration
```bash
AQUA> Check system health, disk usage, and running services
AQUA> Install nginx and configure a reverse proxy
AQUA> Set up a cron job to backup databases daily
AQUA> Manage Docker containers
```

### Development
```bash
AQUA> Clone the repo, create a feature branch, and implement the changes
AQUA> Run tests and fix any failures
AQUA> Deploy to production via Docker
```

### Research & Analysis
```bash
AQUA> Search for latest AI papers and summarize key findings
AQUA> Scrape competitor websites and create a comparison report
AQUA> Analyze CSV data and generate insights
```

### Communication
```bash
AQUA> Send a Slack notification when deployment completes
AQUA> Read my emails and summarize important ones
AQUA> Schedule a meeting for next week
```

## License

MIT
