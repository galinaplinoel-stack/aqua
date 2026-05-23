"""Plugin system tools."""

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class PluginManager:
    """Manages custom tool plugins."""

    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_plugins: dict = {}

    def load_plugin(self, name: str) -> dict:
        """Load a plugin from file."""
        plugin_path = self.plugins_dir / f"{name}.py"
        if not plugin_path.exists():
            return {"error": f"Plugin not found: {name}"}

        try:
            # Add plugins dir to path
            sys.path.insert(0, str(self.plugins_dir))

            # Import module
            spec = importlib.util.spec_from_file_location(name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get tools from plugin
            if hasattr(module, "TOOLS"):
                tools = module.TOOLS
                self.loaded_plugins[name] = {
                    "module": module,
                    "tools": tools,
                    "path": str(plugin_path),
                }
                return {"success": True, "tools": list(tools.keys())}
            else:
                return {"error": "Plugin has no TOOLS dict"}

        except Exception as e:
            return {"error": str(e)}

    def load_all(self) -> list[dict]:
        """Load all plugins from directory."""
        results = []
        for f in self.plugins_dir.glob("*.py"):
            if f.name.startswith("_"):
                continue
            result = self.load_plugin(f.stem)
            results.append({"name": f.stem, **result})
        return results

    def list_plugins(self) -> list[dict]:
        """List available plugins."""
        plugins = []
        for f in self.plugins_dir.glob("*.py"):
            if not f.name.startswith("_"):
                plugins.append({"name": f.stem, "path": str(f)})
        return plugins

    def get_all_tools(self) -> dict:
        """Get all tools from loaded plugins."""
        all_tools = {}
        for name, plugin in self.loaded_plugins.items():
            for tool_name, tool_data in plugin["tools"].items():
                all_tools[f"plugin_{tool_name}"] = tool_data
        return all_tools


_manager = None


def get_plugin_manager() -> PluginManager:
    global _manager
    if _manager is None:
        _manager = PluginManager()
    return _manager


def load_plugin(name: str) -> str:
    """Load a plugin."""
    result = get_plugin_manager().load_plugin(name)
    return json.dumps(result, indent=2)


def list_plugins() -> str:
    """List available plugins."""
    plugins = get_plugin_manager().list_plugins()
    return json.dumps(plugins, indent=2)


PLUGIN_TOOLS = {
    "load_plugin": {
        "func": load_plugin,
        "schema": {
            "type": "function",
            "function": {
                "name": "load_plugin",
                "description": "Load a custom tool plugin.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Plugin name"},
                    },
                    "required": ["name"],
                },
            },
        },
    },
    "list_plugins": {
        "func": list_plugins,
        "schema": {
            "type": "function",
            "function": {
                "name": "list_plugins",
                "description": "List available plugins.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    },
}
