"""Tool registry and execution system."""

import json
import subprocess
from pathlib import Path
from typing import Any, Callable

from rich.console import Console

console = Console()


class Tool:
    """Represents a single tool."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict,
        func: Callable,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    def to_openai_schema(self) -> dict:
        """Convert to OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def execute(self, **kwargs) -> str:
        """Execute the tool with given arguments."""
        try:
            return self.func(**kwargs)
        except Exception as e:
            return f"Error: {e}"


class ToolRegistry:
    """Registry for managing tools."""

    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a tool."""
        self.tools[tool.name] = tool

    def register_dynamic(self, name: str, func: Callable, schema: dict):
        """Register a tool with pre-built schema."""
        self.tools[name] = Tool(
            name=name,
            description=schema["function"]["description"],
            parameters=schema["function"]["parameters"],
            func=func,
        )

    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self.tools.get(name)

    def get_schemas(self) -> list[dict]:
        """Get OpenAI function schemas for all tools."""
        return [tool.to_openai_schema() for tool in self.tools.values()]

    def execute(self, name: str, arguments: str) -> str:
        """Execute a tool by name with JSON arguments."""
        tool = self.get(name)
        if not tool:
            return f"Unknown tool: {name}"

        try:
            args = json.loads(arguments) if isinstance(arguments, str) else arguments
            return tool.execute(**args)
        except json.JSONDecodeError:
            return f"Invalid JSON arguments: {arguments}"


# --- Built-in Tools ---

def shell_exec(command: str) -> str:
    """Execute a shell command and return output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out (30s limit)"


def read_file(path: str) -> str:
    """Read a file and return its contents."""
    p = Path(path)
    if not p.exists():
        return f"Error: File not found: {path}"
    if not p.is_file():
        return f"Error: Not a file: {path}"
    try:
        content = p.read_text(encoding="utf-8")
        if len(content) > 50000:
            return content[:50000] + "\n... (truncated)"
        return content
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    p = Path(path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Written {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def create_default_registry() -> ToolRegistry:
    """Create a registry with built-in tools."""
    registry = ToolRegistry()

    registry.register(Tool(
        name="shell",
        description="Execute a shell command and return its output. Use for running scripts, checking files, system commands, etc.",
        parameters={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute",
                },
            },
            "required": ["command"],
        },
        func=shell_exec,
    ))

    registry.register(Tool(
        name="read_file",
        description="Read the contents of a file at the given path.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read",
                },
            },
            "required": ["path"],
        },
        func=read_file,
    ))

    registry.register(Tool(
        name="write_file",
        description="Write content to a file. Creates parent directories if needed.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["path", "content"],
        },
        func=write_file,
    ))

    return registry
