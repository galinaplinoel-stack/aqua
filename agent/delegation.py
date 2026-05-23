"""Delegation system - task assignment and tracking."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agent.subagent import AgentFactory, SubAgent

console = Console()


class Task:
    """Represents a delegated task."""

    def __init__(
        self,
        task_id: str,
        title: str,
        description: str,
        assigned_to: str,  # agent_id
        assigned_by: str,  # who assigned it
        priority: str = "medium",
        status: str = "pending",
    ):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.assigned_to = assigned_to
        self.assigned_by = assigned_by
        self.priority = priority
        self.status = status
        self.created_at = datetime.now().isoformat()
        self.completed_at: str | None = None
        self.result: str | None = None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "assigned_by": self.assigned_by,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "result": self.result,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        task = cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data["description"],
            assigned_to=data["assigned_to"],
            assigned_by=data["assigned_by"],
            priority=data.get("priority", "medium"),
            status=data.get("status", "pending"),
        )
        task.created_at = data.get("created_at", task.created_at)
        task.completed_at = data.get("completed_at")
        task.result = data.get("result")
        return task


class DelegationManager:
    """Manages task delegation and tracking."""

    def __init__(self, agent_factory: AgentFactory, path: str = "delegations.json"):
        self.agent_factory = agent_factory
        self.path = Path(path)
        self.tasks: dict[str, Task] = {}
        self._load()

    def _load(self):
        """Load tasks from file."""
        if self.path.exists():
            try:
                with open(self.path) as f:
                    data = json.load(f)
                for task_data in data.get("tasks", []):
                    task = Task.from_dict(task_data)
                    self.tasks[task.task_id] = task
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load delegations: {e}[/yellow]")

    def _save(self):
        """Save tasks to file."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "tasks": [task.to_dict() for task in self.tasks.values()]
            }
            with open(self.path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[red]Error saving delegations: {e}[/red]")

    def delegate_task(
        self,
        title: str,
        description: str,
        agent_id: str,
        assigned_by: str = "CEO",
        priority: str = "medium",
    ) -> Task:
        """Delegate a task to an agent."""
        agent = self.agent_factory.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")

        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            assigned_to=agent_id,
            assigned_by=assigned_by,
            priority=priority,
        )

        self.tasks[task_id] = task
        self._save()

        console.print(f"[green]Task '{title}' delegated to {agent.name} ({agent.role})[/green]")
        return task

    def execute_task(self, task_id: str) -> str:
        """Execute a delegated task."""
        task = self.tasks.get(task_id)
        if not task:
            return f"Task not found: {task_id}"

        if task.status != "pending":
            return f"Task already {task.status}"

        agent = self.agent_factory.get_agent(task.assigned_to)
        if not agent:
            return f"Agent not found: {task.assigned_to}"

        # Update status
        task.status = "in_progress"
        self._save()

        # Execute
        console.print(f"[dim]Executing task: {task.title}[/dim]")
        result = agent.execute_task(
            f"Task: {task.title}\n\n{task.description}"
        )

        # Update task
        task.status = "completed"
        task.completed_at = datetime.now().isoformat()
        task.result = result
        self._save()

        return result

    def get_pending_tasks(self, agent_id: str | None = None) -> list[Task]:
        """Get pending tasks, optionally filtered by agent."""
        tasks = [t for t in self.tasks.values() if t.status == "pending"]
        if agent_id:
            tasks = [t for t in tasks if t.assigned_to == agent_id]
        return tasks

    def get_task_status(self, task_id: str) -> dict | None:
        """Get task status."""
        task = self.tasks.get(task_id)
        if task:
            return task.to_dict()
        return None

    def display_tasks(self, agent_id: str | None = None):
        """Display tasks in a table."""
        tasks = list(self.tasks.values())
        if agent_id:
            tasks = [t for t in tasks if t.assigned_to == agent_id]

        if not tasks:
            console.print("[dim]No tasks found[/dim]")
            return

        table = Table(title="Delegated Tasks")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="cyan")
        table.add_column("Assigned To", style="green")
        table.add_column("Priority")
        table.add_column("Status")
        table.add_column("Created")

        for task in tasks:
            agent = self.agent_factory.get_agent(task.assigned_to)
            agent_name = agent.name if agent else task.assigned_to

            priority_color = {
                "high": "red",
                "medium": "yellow",
                "low": "green",
            }.get(task.priority, "white")

            status_color = {
                "pending": "yellow",
                "in_progress": "blue",
                "completed": "green",
                "failed": "red",
            }.get(task.status, "white")

            table.add_row(
                task.task_id,
                task.title,
                agent_name,
                f"[{priority_color}]{task.priority}[/{priority_color}]",
                f"[{status_color}]{task.status}[/{status_color}]",
                task.created_at[:16],
            )

        console.print(table)
