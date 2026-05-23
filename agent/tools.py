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

    def register_batch(self, tools_dict: dict):
        """Register multiple tools from a dict."""
        for name, tool_data in tools_dict.items():
            self.register_dynamic(name, tool_data["func"], tool_data["schema"])

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

    def list_tools(self) -> list[dict]:
        """List all registered tools."""
        return [
            {"name": t.name, "description": t.description}
            for t in self.tools.values()
        ]


def create_registry(categories: list[str] | None = None) -> ToolRegistry:
    """Create a tool registry with specified categories."""
    from agent.tools import ALL_TOOL_CATEGORIES, get_all_tools

    registry = ToolRegistry()

    if categories:
        for cat in categories:
            if cat in ALL_TOOL_CATEGORIES:
                registry.register_batch(ALL_TOOL_CATEGORIES[cat])
    else:
        registry.register_batch(get_all_tools())

    return registry
