# AQUA

**Enterprise-grade Multi-Agent Framework with Full VPS Management**

AQUA is a powerful AI agent framework built in Python that simulates a real company structure. It features interactive chat, **80+ built-in tools**, persistent memory, persona management, and a complete multi-agent hierarchy system where AI agents can create, manage, and delegate tasks to specialized sub-agents — all through a clean CLI interface.

## Quick Start

```bash
# Clone repo
git clone https://github.com/galinaplinoel-stack/aqua.git
cd aqua

# Create virtual environment (required for Python 3.12+)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Option 1: Quick setup (one command)
python3 main.py --quick-setup YOUR_API_KEY openai

# Option 2: Interactive wizard
python3 main.py --setup

# Run AQUA
python3 main.py
```

### Supported Providers

```bash
# OpenAI
python3 main.py --quick-setup sk-xxxxx openai

# OpenRouter
python3 main.py --quick-setup sk-xxxxx openrouter

# Together AI
python3 main.py --quick-setup sk-xxxxx together

# Groq (fast)
python3 main.py --quick-setup sk-xxxxx groq

# Xiaomi MiMo
python3 main.py --quick-setup sk-xxxxx mimo
```

### Config Commands

```bash
# Show current config
python3 main.py --config

# Set specific values
python3 main.py --config provider.api_key sk-new-key
python3 main.py --config provider.model gpt-4-turbo
python3 main.py --config persona.name "MyBot"

# List providers
python3 main.py --providers
```

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
- 🤖 **Autonomous Operation** — AI can create agents and delegate tasks
- 🔐 **Role-Based Permissions** — Control what each agent can do

## Tool Categories (80+ Tools)

### 🌐 Web & Scraping
- `web_search` — Search the web (DuckDuckGo)
- `scrape_webpage` — Extract content from websites
- `extract_links` — Get all links from a page

### 🔌 HTTP & API
- `http_request` — Full HTTP client (GET, POST, PUT, DELETE)
- `api_get`, `api_post`, `api_put` — Simple API calls
- `download_file` — Download files from URLs

### 💻 Code Execution
- `run_python` — Execute Python code
- `run_shell` — Run shell commands (full access)
- `run_script` — Execute script files

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

### 🖥️ Terminal & VPS Management (Full Access)
- `system_info` — System information (OS, CPU, memory, disk)
- `process_list` — List running processes
- `service_manage` — Manage systemd services
- `firewall_manage` — UFW firewall rules
- `user_manage` — System user management
- `cron_manage` — Cron job management
- `network_info` — Network interfaces and ports
- `install_package` — Package installation
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
- `add_calendar_event`, `list_calendar_events` — Calendar management

### 🔌 Plugins
- `load_plugin`, `list_plugins` — Custom tool plugins

### 🔐 Authentication
- `set_credential`, `get_credential` — Secure credential storage

### 🧠 Vector Memory
- `add_memory`, `search_memory` — Semantic memory search

## CLI Commands

### Chat Commands
- `/help` — Show all commands
- `/clear` — Clear conversation history
- `/reload` — Reload persona from `Aqua.md`
- `/history` — Show message count
- `/tools [category]` — List tools
- `/remember X` — Save a fact to memory
- `/memory` — Show memory stats
- `/search X` — Search memory
- `/quit` — Exit

### Agent Management
- `/agents` — List all agents
- `/create NAME ROLE DEPT DESC` — Create new agent
- `/assign TITLE DESC AGENT_ID` — Assign task
- `/tasks [AGENT_ID]` — List tasks
- `/execute TASK_ID` — Execute task
- `/orgchart` — Show company structure
- `/departments` — List departments

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

### Usage Examples

```bash
# Create an agent
AQUA> /create Alice "Senior Developer" Engineering "Leads backend"

# Assign a task
AQUA> /assign "Build API" "Create REST API" senior_developer_xxx

# Execute the task
AQUA> /execute task_xxx

# Autonomous mode
AQUA> Create a developer agent and have it write a weather API
```

## Configuration

Edit `config/config.yaml`:

```yaml
provider:
  base_url: "https://api.openai.com/v1"
  api_key: "your-key"
  model: "gpt-4o"

persona:
  name: "AQUA"
  path: "Aqua.md"

memory:
  enabled: true
  path: "memory.json"

tools:
  enabled: true
  categories: []  # Empty = load all

hierarchy:
  enabled: true
  path: "hierarchy.json"
```

## Architecture

```
aqua/
├── Aqua.md                    # Persona file (user-editable)
├── agent/
│   ├── core.py                # Chat engine
│   ├── tools/                 # 80+ tools in 16 categories
│   ├── memory.py              # Persistent memory
│   ├── persona.py             # Loads Aqua.md
│   ├── hierarchy.py           # Company structure
│   ├── subagent.py            # Sub-agent system
│   ├── delegation.py          # Task delegation
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

- **Python 3.10+**
- **openai** — LLM API client
- **prompt_toolkit** — Interactive CLI
- **rich** — Formatted output
- **pyyaml** — Configuration
- **requests** — HTTP client
- **beautifulsoup4** — Web scraping
- **PyMuPDF** — PDF processing
- **pandas** — Data processing
- **python-telegram-bot** — Telegram integration

## License

MIT
