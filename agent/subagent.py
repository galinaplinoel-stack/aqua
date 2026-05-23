"""Sub-agent system - specialized agents with roles."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

from agent.memory import Memory
from agent.persona import Persona
from agent.tools import ToolRegistry

console = Console()


class SubAgent:
    """A specialized agent with a specific role."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        department: str,
        description: str,
        permissions: list[str],
        client: OpenAI,
        model: str,
        tools: ToolRegistry | None = None,
        memory: Memory | None = None,
        parent_id: str | None = None,
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.department = department
        self.description = description
        self.permissions = permissions
        self.client = client
        self.model = model
        self.tools = tools
        self.memory = memory
        self.parent_id = parent_id
        self.messages: list[dict] = []
        self.created_at = datetime.now().isoformat()
        self.tasks_completed = 0

        # Build system prompt
        self._init_system_prompt()

    def _init_system_prompt(self):
        """Initialize the agent's system prompt based on role."""
        prompt_parts = [
            f"You are {self.name}, a {self.role} in the {self.department} department.",
            f"",
            f"## Your Role",
            f"{self.description}",
            f"",
            f"## Permissions",
            f"You can: {', '.join(self.permissions)}",
            f"",
            f"## Guidelines",
            f"- Stay focused on your role and responsibilities",
            f"- Report results clearly and concisely",
            f"- Ask for clarification if a task is unclear",
            f"- Collaborate with other agents when needed",
        ]

        if self.memory:
            context = self.memory.get_context_string()
            if context:
                prompt_parts.append(f"\n{context}")

        self.messages = [{"role": "system", "content": "\n".join(prompt_parts)}]

    def execute_task(self, task: str) -> str:
        """Execute a task and return the result."""
        if not task:
            return "No task provided"

        self.messages.append({"role": "user", "content": task})

        try:
            kwargs = {"model": self.model, "messages": self.messages}
            if self.tools:
                kwargs["tools"] = self.tools.get_schemas()

            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message

            # Handle tool calls
            if message.tool_calls:
                self.messages.append(message.model_dump())

                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = tool_call.function.arguments

                    if self.tools:
                        result = self.tools.execute(func_name, func_args)
                    else:
                        result = "Error: Tools not available"

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })

                # Continue after tool execution
                return self.execute_task("")

            result = message.content or ""
            self.messages.append({"role": "assistant", "content": result})
            self.tasks_completed += 1

            return result

        except Exception as e:
            return f"Error: {e}"

    def get_status(self) -> dict:
        """Get agent status."""
        return {
            "id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "tasks_completed": self.tasks_completed,
            "created_at": self.created_at,
        }


class AgentFactory:
    """Creates and manages sub-agents."""

    def __init__(
        self,
        client: OpenAI | None,
        model: str,
        tools: ToolRegistry | None = None,
        memory_path: str = "agents",
    ):
        self.client = client
        self.model = model
        self.tools = tools
        self.memory_path = Path(memory_path)
        self.agents: dict[str, SubAgent] = {}
        self._load_agents()

    def _load_agents(self):
        """Load existing agents from disk."""
        if not self.memory_path.exists():
            return

        for agent_dir in self.memory_path.iterdir():
            if agent_dir.is_dir():
                config_file = agent_dir / "config.json"
                if config_file.exists():
                    try:
                        with open(config_file) as f:
                            config = json.load(f)
                        if self.client:
                            self._create_agent_from_config(config)
                    except Exception as e:
                        console.print(f"[dim]Could not load agent {agent_dir.name}: {e}[/dim]")

    def _create_agent_from_config(self, config: dict) -> SubAgent:
        """Create an agent from saved config."""
        agent_memory = Memory(
            path=str(self.memory_path / config["agent_id"] / "memory.json"),
            enabled=True,
        )

        agent = SubAgent(
            agent_id=config["agent_id"],
            name=config["name"],
            role=config["role"],
            department=config["department"],
            description=config["description"],
            permissions=config["permissions"],
            client=self.client,
            model=self.model,
            tools=self.tools,
            memory=agent_memory,
            parent_id=config.get("parent_id"),
        )

        self.agents[agent.agent_id] = agent
        return agent

    def create_agent(
        self,
        name: str,
        role: str,
        department: str,
        description: str,
        permissions: list[str] | None = None,
        parent_id: str | None = None,
    ) -> SubAgent:
        """Create a new sub-agent."""
        if not self.client:
            raise ValueError("Client not initialized. Set client before creating agents.")

        agent_id = f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

        # Create agent memory directory
        agent_dir = self.memory_path / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Create agent memory
        agent_memory = Memory(
            path=str(agent_dir / "memory.json"),
            enabled=True,
        )

        # Default permissions based on role
        if permissions is None:
            permissions = ["read_files", "write_files"]

        agent = SubAgent(
            agent_id=agent_id,
            name=name,
            role=role,
            department=department,
            description=description,
            permissions=permissions,
            client=self.client,
            model=self.model,
            tools=self.tools,
            memory=agent_memory,
            parent_id=parent_id,
        )

        # Save agent config
        config = {
            "agent_id": agent_id,
            "name": name,
            "role": role,
            "department": department,
            "description": description,
            "permissions": permissions,
            "parent_id": parent_id,
            "created_at": agent.created_at,
        }
        with open(agent_dir / "config.json", "w") as f:
            json.dump(config, f, indent=2)

        self.agents[agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> SubAgent | None:
        """Get an agent by ID."""
        return self.agents.get(agent_id)

    def list_agents(self) -> list[dict]:
        """List all agents."""
        return [agent.get_status() for agent in self.agents.values()]

    def delete_agent(self, agent_id: str):
        """Delete an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            # Remove agent directory
            agent_dir = self.memory_path / agent_id
            if agent_dir.exists():
                import shutil
                shutil.rmtree(agent_dir)

    def get_agents_by_department(self, department: str) -> list[SubAgent]:
        """Get all agents in a department."""
        return [a for a in self.agents.values() if a.department == department]

    def get_agents_by_role(self, role: str) -> list[SubAgent]:
        """Get all agents with a specific role."""
        return [a for a in self.agents.values() if a.role == role]
