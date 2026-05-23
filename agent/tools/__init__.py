"""AQUA Tools - Comprehensive tool collection."""

import json
from typing import Callable

from agent.tools.web import WEB_SEARCH_TOOLS
from agent.tools.http import HTTP_TOOLS
from agent.tools.code_exec import CODE_EXEC_TOOLS
from agent.tools.git import GIT_TOOLS
from agent.tools.database import DATABASE_TOOLS
from agent.tools.file_formats import FILE_FORMAT_TOOLS
from agent.tools.email import EMAIL_TOOLS
from agent.tools.terminal import VPS_TOOLS
from agent.tools.monitoring import MONITORING_TOOLS
from agent.tools.caching import CACHING_TOOLS
from agent.tools.workflow import WORKFLOW_TOOLS
from agent.tools.notifications import NOTIFICATION_TOOLS
from agent.tools.calendar import CALENDAR_TOOLS
from agent.tools.plugins import PLUGIN_TOOLS
from agent.tools.auth import AUTH_TOOLS
from agent.tools.vector_memory import VECTOR_MEMORY_TOOLS


# All tool categories
ALL_TOOL_CATEGORIES = {
    "web": WEB_SEARCH_TOOLS,
    "http": HTTP_TOOLS,
    "code_exec": CODE_EXEC_TOOLS,
    "git": GIT_TOOLS,
    "database": DATABASE_TOOLS,
    "file_formats": FILE_FORMAT_TOOLS,
    "email": EMAIL_TOOLS,
    "terminal": VPS_TOOLS,
    "monitoring": MONITORING_TOOLS,
    "caching": CACHING_TOOLS,
    "workflow": WORKFLOW_TOOLS,
    "notifications": NOTIFICATION_TOOLS,
    "calendar": CALENDAR_TOOLS,
    "plugins": PLUGIN_TOOLS,
    "auth": AUTH_TOOLS,
    "vector_memory": VECTOR_MEMORY_TOOLS,
}


def get_all_tools() -> dict:
    """Get all tools merged into one dict."""
    all_tools = {}
    for category_tools in ALL_TOOL_CATEGORIES.values():
        all_tools.update(category_tools)
    return all_tools


def get_tools_by_category(category: str) -> dict:
    """Get tools for a specific category."""
    return ALL_TOOL_CATEGORIES.get(category, {})


# Tool class
class Tool:
    """Represents a single tool."""

    def __init__(self, name: str, description: str, parameters: dict, func: Callable):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    def to_openai_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def execute(self, **kwargs) -> str:
        try:
            return self.func(**kwargs)
        except Exception as e:
            return f"Error: {e}"


# ToolRegistry class
class ToolRegistry:
    """Registry for managing tools."""

    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def register_dynamic(self, name: str, func: Callable, schema: dict):
        self.tools[name] = Tool(
            name=name,
            description=schema["function"]["description"],
            parameters=schema["function"]["parameters"],
            func=func,
        )

    def register_batch(self, tools_dict: dict):
        for name, tool_data in tools_dict.items():
            self.register_dynamic(name, tool_data["func"], tool_data["schema"])

    def get(self, name: str) -> Tool | None:
        return self.tools.get(name)

    def get_schemas(self) -> list[dict]:
        return [tool.to_openai_schema() for tool in self.tools.values()]

    def execute(self, name: str, arguments: str) -> str:
        tool = self.get(name)
        if not tool:
            return f"Unknown tool: {name}"
        try:
            args = json.loads(arguments) if isinstance(arguments, str) else arguments
            return tool.execute(**args)
        except json.JSONDecodeError:
            return f"Invalid JSON arguments: {arguments}"

    def list_tools(self) -> list[dict]:
        return [{"name": t.name, "description": t.description} for t in self.tools.values()]


def create_registry(categories: list[str] | None = None) -> ToolRegistry:
    """Create a tool registry with specified categories."""
    registry = ToolRegistry()

    if categories:
        for cat in categories:
            if cat in ALL_TOOL_CATEGORIES:
                registry.register_batch(ALL_TOOL_CATEGORIES[cat])
    else:
        registry.register_batch(get_all_tools())

    return registry
