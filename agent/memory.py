"""Persistent memory system - JSON-based storage with search."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console

console = Console()


class Memory:
    """Persistent memory storage using JSON."""

    def __init__(self, path: str = "memory.json", enabled: bool = True):
        self.path = Path(path)
        self.enabled = enabled
        self.data: dict[str, Any] = {
            "facts": [],
            "conversations": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "sessions": 0,
            },
        }
        if self.enabled:
            self._load()

    def _load(self):
        """Load memory from file."""
        if self.path.exists():
            try:
                with open(self.path) as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                console.print(f"[yellow]Warning: Could not load memory: {e}[/yellow]")

    def _save(self):
        """Save memory to file."""
        if not self.enabled:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[red]Error saving memory: {e}[/red]")

    def add_fact(self, fact: str, category: str = "general"):
        """Add a memorable fact."""
        entry = {
            "fact": fact,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["facts"].append(entry)
        self._save()

    def add_conversation_summary(self, summary: str, message_count: int):
        """Save a conversation summary."""
        entry = {
            "summary": summary,
            "message_count": message_count,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["conversations"].append(entry)
        # Keep only last 50 conversations
        self.data["conversations"] = self.data["conversations"][-50:]
        self._save()

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Search memory by keyword."""
        query_lower = query.lower()
        results = []

        # Search facts
        for fact in self.data["facts"]:
            if query_lower in fact["fact"].lower():
                results.append({
                    "type": "fact",
                    "content": fact["fact"],
                    "category": fact["category"],
                    "timestamp": fact["timestamp"],
                })

        # Search conversations
        for conv in self.data["conversations"]:
            if query_lower in conv["summary"].lower():
                results.append({
                    "type": "conversation",
                    "content": conv["summary"],
                    "timestamp": conv["timestamp"],
                })

        return results[:limit]

    def get_recent_facts(self, limit: int = 10) -> list[dict]:
        """Get most recent facts."""
        return self.data["facts"][-limit:]

    def get_stats(self) -> dict:
        """Get memory statistics."""
        return {
            "facts": len(self.data["facts"]),
            "conversations": len(self.data["conversations"]),
            "sessions": self.data["metadata"].get("sessions", 0),
            "created": self.data["metadata"].get("created", "unknown"),
        }

    def increment_sessions(self):
        """Increment session counter."""
        self.data["metadata"]["sessions"] = self.data["metadata"].get("sessions", 0) + 1
        self.data["metadata"]["last_session"] = datetime.now().isoformat()
        self._save()

    def clear(self):
        """Clear all memory."""
        self.data = {
            "facts": [],
            "conversations": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "sessions": 0,
            },
        }
        self._save()

    def get_context_string(self, max_facts: int = 10) -> str:
        """Get memory context as string for system prompt injection."""
        if not self.enabled or not self.data["facts"]:
            return ""

        recent_facts = self.data["facts"][-max_facts:]
        lines = ["## Known Facts"]
        for fact in recent_facts:
            lines.append(f"- [{fact['category']}] {fact['fact']}")

        return "\n".join(lines)
