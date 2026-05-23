"""Calendar and scheduling tools."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class Calendar:
    """Simple file-based calendar."""

    def __init__(self, path: str = "calendar.json"):
        self.path = Path(path)
        self.events: list[dict] = []
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path) as f:
                    self.events = json.load(f)
            except:
                self.events = []

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.events, f, indent=2)

    def add_event(self, title: str, start: str, end: Optional[str] = None, description: str = "") -> dict:
        """Add a calendar event."""
        event = {
            "id": len(self.events) + 1,
            "title": title,
            "start": start,
            "end": end or start,
            "description": description,
            "created_at": datetime.now().isoformat(),
        }
        self.events.append(event)
        self._save()
        return event

    def list_events(self, date: Optional[str] = None) -> list[dict]:
        """List events, optionally filtered by date."""
        if date:
            return [e for e in self.events if e["start"].startswith(date)]
        return self.events

    def delete_event(self, event_id: int) -> bool:
        """Delete an event by ID."""
        self.events = [e for e in self.events if e["id"] != event_id]
        self._save()
        return True


_calendar = None


def get_calendar() -> Calendar:
    global _calendar
    if _calendar is None:
        _calendar = Calendar()
    return _calendar


def add_calendar_event(title: str, start: str, end: Optional[str] = None, description: str = "") -> str:
    """Add an event to the calendar."""
    event = get_calendar().add_event(title, start, end, description)
    return json.dumps(event, indent=2)


def list_calendar_events(date: Optional[str] = None) -> str:
    """List calendar events."""
    events = get_calendar().list_events(date)
    return json.dumps(events, indent=2)


def delete_calendar_event(event_id: int) -> str:
    """Delete a calendar event."""
    get_calendar().delete_event(event_id)
    return f"Event {event_id} deleted"


CALENDAR_TOOLS = {
    "add_calendar_event": {
        "func": add_calendar_event,
        "schema": {
            "type": "function",
            "function": {
                "name": "add_calendar_event",
                "description": "Add an event to the calendar.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Event title"},
                        "start": {"type": "string", "description": "Start time (ISO format)"},
                        "end": {"type": "string", "description": "End time (ISO format)"},
                        "description": {"type": "string", "description": "Event description"},
                    },
                    "required": ["title", "start"],
                },
            },
        },
    },
    "list_calendar_events": {
        "func": list_calendar_events,
        "schema": {
            "type": "function",
            "function": {
                "name": "list_calendar_events",
                "description": "List calendar events.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "Filter by date (YYYY-MM-DD)"},
                    },
                },
            },
        },
    },
    "delete_calendar_event": {
        "func": delete_calendar_event,
        "schema": {
            "type": "function",
            "function": {
                "name": "delete_calendar_event",
                "description": "Delete a calendar event.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "integer", "description": "Event ID"},
                    },
                    "required": ["event_id"],
                },
            },
        },
    },
}
