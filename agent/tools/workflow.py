"""Workflow engine tools."""

import json
import time
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class WorkflowEngine:
    """Simple workflow engine."""

    def __init__(self, path: str = "workflows.json"):
        self.path = Path(path)
        self.workflows: dict = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path) as f:
                    self.workflows = json.load(f)
            except:
                self.workflows = {}

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.workflows, f, indent=2)

    def create(self, name: str, steps: list[dict]) -> dict:
        """Create a workflow."""
        workflow = {
            "name": name,
            "steps": steps,
            "status": "created",
            "current_step": 0,
            "created_at": time.time(),
            "results": [],
        }
        self.workflows[name] = workflow
        self._save()
        return workflow

    def get(self, name: str) -> Optional[dict]:
        """Get a workflow."""
        return self.workflows.get(name)

    def list_all(self) -> list[dict]:
        """List all workflows."""
        return [
            {"name": w["name"], "status": w["status"], "steps": len(w["steps"])}
            for w in self.workflows.values()
        ]

    def update_step(self, name: str, step_index: int, result: str):
        """Update a step result."""
        if name in self.workflows:
            wf = self.workflows[name]
            if step_index < len(wf["steps"]):
                wf["steps"][step_index]["result"] = result
                wf["steps"][step_index]["status"] = "completed"
                wf["results"].append({"step": step_index, "result": result})
                if step_index + 1 < len(wf["steps"]):
                    wf["current_step"] = step_index + 1
                    wf["status"] = "in_progress"
                else:
                    wf["status"] = "completed"
                self._save()


_engine = None


def get_engine() -> WorkflowEngine:
    global _engine
    if _engine is None:
        _engine = WorkflowEngine()
    return _engine


def create_workflow(name: str, steps_json: str) -> str:
    """Create a workflow with steps."""
    try:
        steps = json.loads(steps_json)
        workflow = get_engine().create(name, steps)
        return json.dumps(workflow, indent=2)
    except Exception as e:
        return f"Error: {e}"


def list_workflows() -> str:
    """List all workflows."""
    workflows = get_engine().list_all()
    return json.dumps(workflows, indent=2)


def get_workflow(name: str) -> str:
    """Get workflow details."""
    workflow = get_engine().get(name)
    if workflow:
        return json.dumps(workflow, indent=2)
    return f"Workflow not found: {name}"


WORKFLOW_TOOLS = {
    "create_workflow": {
        "func": create_workflow,
        "schema": {
            "type": "function",
            "function": {
                "name": "create_workflow",
                "description": "Create a workflow with steps.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Workflow name"},
                        "steps_json": {"type": "string", "description": "JSON array of steps"},
                    },
                    "required": ["name", "steps_json"],
                },
            },
        },
    },
    "list_workflows": {
        "func": list_workflows,
        "schema": {
            "type": "function",
            "function": {
                "name": "list_workflows",
                "description": "List all workflows.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    },
    "get_workflow": {
        "func": get_workflow,
        "schema": {
            "type": "function",
            "function": {
                "name": "get_workflow",
                "description": "Get workflow details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Workflow name"},
                    },
                    "required": ["name"],
                },
            },
        },
    },
}
