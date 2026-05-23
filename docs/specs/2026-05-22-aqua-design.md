# AQUA — Design Spec

**Date:** 2026-05-22
**Status:** Pending Approval
**Author:** Furina + Bocchi

## Overview

AQUA is a simple, modular AI Agent CLI built in Python. It provides interactive chat, tool execution, persistent memory, and persona management through a clean terminal interface.

## Goals

- Lightweight and easy to understand
- Modular architecture (easy to add features later)
- OpenAI-compatible API (works with any provider that supports OpenAI format)
- Clean CLI experience with rich output

## Architecture

### Core Components

1. **Core (agent/core.py)** — Chat loop, LLM interaction, message handling
2. **Tools (agent/tools.py)** — Tool registry, function calling, execution
3. **Memory (agent/memory.py)** — Persistent memory via JSON file
4. **Persona (agent/persona.py)** — System prompt management, loads `Aqua.md`
5. **CLI (cli.py)** — Interactive terminal interface
6. **Config (config/config.yaml)** — All settings in one file

### Config Format

```yaml
provider:
  base_url: "https://api.openai.com/v1"
  api_key: "your-key"
  model: "gpt-4o"

persona:
  name: "AQUA"
  path: "Aqua.md"  # Edit this file to customize personality

memory:
  enabled: true
  path: "memory.json"

tools:
  enabled: true
  builtin:
    - shell
    - read_file
    - write_file
```

### Phases

**Phase 1 — MVP:**
- Interactive chat loop
- System prompt / persona
- OpenAI-compatible API connection
- Basic CLI with prompt_toolkit

**Phase 2 — Tools:**
- Tool registry system
- Function calling support
- Built-in tools: shell, read_file, write_file

**Phase 3 — Memory:**
- Persistent memory (JSON)
- Auto-save conversation context
- Memory search

**Phase 4 — Platforms:**
- Telegram integration
- Gateway system

## Tech Stack

- Python 3.10+
- openai SDK
- prompt_toolkit
- rich
- pyyaml

## File Structure

```
aqua/
├── Aqua.md              # Persona file (user-editable)
├── agent/
│   ├── __init__.py
│   ├── core.py
│   ├── tools.py
│   ├── memory.py
│   └── persona.py
├── config/
│   └── config.yaml
├── docs/
│   └── specs/
│       └── 2026-05-22-aqua-design.md
├── cli.py
├── main.py
└── requirements.txt
```

## Key Principles

- **Simple first** — Start minimal, expand later
- **Modular** — Each component is independent
- **Config-driven** — Everything configurable via YAML
- **OpenAI-compatible** — Works with any OpenAI-format API
