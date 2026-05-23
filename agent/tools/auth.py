"""Authentication manager tools."""

import json
import os
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class AuthManager:
    """Manages API keys and credentials."""

    def __init__(self, path: str = ".auth.json"):
        self.path = Path(path)
        self.credentials: dict = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path) as f:
                    self.credentials = json.load(f)
            except:
                self.credentials = {}

    def _save(self):
        # Secure the file
        with open(self.path, "w") as f:
            json.dump(self.credentials, f, indent=2)
        os.chmod(self.path, 0o600)

    def set_credential(self, service: str, key: str, value: str):
        """Set a credential."""
        if service not in self.credentials:
            self.credentials[service] = {}
        self.credentials[service][key] = value
        self._save()

    def get_credential(self, service: str, key: str) -> Optional[str]:
        """Get a credential."""
        return self.credentials.get(service, {}).get(key)

    def list_services(self) -> list[str]:
        """List all services."""
        return list(self.credentials.keys())

    def list_keys(self, service: str) -> list[str]:
        """List keys for a service."""
        return list(self.credentials.get(service, {}).keys())

    def delete_credential(self, service: str, key: str) -> bool:
        """Delete a credential."""
        if service in self.credentials and key in self.credentials[service]:
            del self.credentials[service][key]
            if not self.credentials[service]:
                del self.credentials[service]
            self._save()
            return True
        return False


_manager = None


def get_auth_manager() -> AuthManager:
    global _manager
    if _manager is None:
        _manager = AuthManager()
    return _manager


def set_credential(service: str, key: str, value: str) -> str:
    """Set a credential."""
    get_auth_manager().set_credential(service, key, value)
    return f"Credential set: {service}.{key}"


def get_credential(service: str, key: str) -> str:
    """Get a credential."""
    value = get_auth_manager().get_credential(service, key)
    if value:
        return value
    return f"Credential not found: {service}.{key}"


def list_credentials(service: Optional[str] = None) -> str:
    """List credentials."""
    manager = get_auth_manager()
    if service:
        keys = manager.list_keys(service)
        return json.dumps({service: keys}, indent=2)
    else:
        services = manager.list_services()
        result = {}
        for s in services:
            result[s] = manager.list_keys(s)
        return json.dumps(result, indent=2)


AUTH_TOOLS = {
    "set_credential": {
        "func": set_credential,
        "schema": {
            "type": "function",
            "function": {
                "name": "set_credential",
                "description": "Set a credential (API key, token, password).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service": {"type": "string", "description": "Service name (e.g., 'github', 'aws')"},
                        "key": {"type": "string", "description": "Credential key (e.g., 'api_key', 'token')"},
                        "value": {"type": "string", "description": "Credential value"},
                    },
                    "required": ["service", "key", "value"],
                },
            },
        },
    },
    "get_credential": {
        "func": get_credential,
        "schema": {
            "type": "function",
            "function": {
                "name": "get_credential",
                "description": "Get a credential value.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service": {"type": "string", "description": "Service name"},
                        "key": {"type": "string", "description": "Credential key"},
                    },
                    "required": ["service", "key"],
                },
            },
        },
    },
    "list_credentials": {
        "func": list_credentials,
        "schema": {
            "type": "function",
            "function": {
                "name": "list_credentials",
                "description": "List stored credentials.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service": {"type": "string", "description": "Filter by service"},
                    },
                },
            },
        },
    },
}
