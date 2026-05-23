"""Delegation tools - tools for agent creation and task delegation."""

import json
from typing import Any

from agent.delegation import DelegationManager
from agent.hierarchy import Hierarchy
from agent.subagent import AgentFactory


def create_delegation_tools(
    agent_factory: AgentFactory,
    hierarchy: Hierarchy,
    delegation_manager: DelegationManager,
) -> dict:
    """Create tools for delegation and agent management."""

    def create_agent(
        name: str,
        role: str,
        department: str,
        description: str,
        permissions: str = "read_files,write_files",
    ) -> str:
        """Create a new agent with a specific role in the company."""
        try:
            # Validate department exists
            if department not in hierarchy.departments:
                available = ", ".join(hierarchy.departments.keys())
                return f"Department '{department}' not found. Available: {available}"

            # Parse permissions
            perm_list = [p.strip() for p in permissions.split(",")]

            # Create agent
            agent = agent_factory.create_agent(
                name=name,
                role=role,
                department=department,
                description=description,
                permissions=perm_list,
            )

            return json.dumps({
                "success": True,
                "agent_id": agent.agent_id,
                "name": agent.name,
                "role": agent.role,
                "department": agent.department,
                "message": f"Agent '{name}' created as {role} in {department}",
            }, indent=2)

        except Exception as e:
            return f"Error creating agent: {e}"

    def delegate_task(
        title: str,
        description: str,
        agent_id: str,
        priority: str = "medium",
    ) -> str:
        """Delegate a task to an existing agent."""
        try:
            task = delegation_manager.delegate_task(
                title=title,
                description=description,
                agent_id=agent_id,
                priority=priority,
            )

            return json.dumps({
                "success": True,
                "task_id": task.task_id,
                "title": task.title,
                "assigned_to": task.assigned_to,
                "message": f"Task '{title}' delegated to agent {agent_id}",
            }, indent=2)

        except Exception as e:
            return f"Error delegating task: {e}"

    def execute_task(task_id: str) -> str:
        """Execute a delegated task."""
        try:
            result = delegation_manager.execute_task(task_id)
            return result
        except Exception as e:
            return f"Error executing task: {e}"

    def list_agents() -> str:
        """List all agents in the company."""
        agents = agent_factory.list_agents()
        if not agents:
            return "No agents found. Use create_agent to create one."

        return json.dumps(agents, indent=2)

    def list_tasks(agent_id: str = "") -> str:
        """List delegated tasks, optionally filtered by agent."""
        tasks = delegation_manager.get_pending_tasks(agent_id if agent_id else None)
        if not tasks:
            return "No pending tasks found."

        return json.dumps([t.to_dict() for t in tasks], indent=2)

    def get_company_structure() -> str:
        """Get the company organizational structure."""
        return hierarchy.to_system_prompt() or "No company structure defined."

    def list_departments() -> str:
        """List all departments and their roles."""
        if not hierarchy.departments:
            return "No departments defined."

        result = []
        for name, dept in hierarchy.departments.items():
            result.append(f"## {name}")
            result.append(f"_{dept.description}_")
            if dept.head:
                result.append(f"Head: {dept.head}")
            for role_name, role in dept.roles.items():
                result.append(f"- **{role_name}**: {role.description}")
            result.append("")

        return "\n".join(result)

    return {
        "create_agent": {
            "func": create_agent,
            "schema": {
                "type": "function",
                "function": {
                    "name": "create_agent",
                    "description": "Create a new AI agent with a specific role in the company. The agent can then be delegated tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the agent (e.g., 'Alice', 'DevBot')",
                            },
                            "role": {
                                "type": "string",
                                "description": "Role/position (e.g., 'Senior Developer', 'Product Manager')",
                            },
                            "department": {
                                "type": "string",
                                "description": "Department name (e.g., 'Engineering', 'Product')",
                            },
                            "description": {
                                "type": "string",
                                "description": "What this agent does and its responsibilities",
                            },
                            "permissions": {
                                "type": "string",
                                "description": "Comma-separated list of permissions (default: 'read_files,write_files')",
                            },
                        },
                        "required": ["name", "role", "department", "description"],
                    },
                },
            },
        },
        "delegate_task": {
            "func": delegate_task,
            "schema": {
                "type": "function",
                "function": {
                    "name": "delegate_task",
                    "description": "Delegate a task to an existing agent. The agent will execute the task when you call execute_task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Short title for the task",
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of what needs to be done",
                            },
                            "agent_id": {
                                "type": "string",
                                "description": "ID of the agent to delegate to",
                            },
                            "priority": {
                                "type": "string",
                                "description": "Task priority: 'high', 'medium', or 'low'",
                                "enum": ["high", "medium", "low"],
                            },
                        },
                        "required": ["title", "description", "agent_id"],
                    },
                },
            },
        },
        "execute_task": {
            "func": execute_task,
            "schema": {
                "type": "function",
                "function": {
                    "name": "execute_task",
                    "description": "Execute a delegated task. The assigned agent will work on it and return the result.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "ID of the task to execute",
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            },
        },
        "list_agents": {
            "func": list_agents,
            "schema": {
                "type": "function",
                "function": {
                    "name": "list_agents",
                    "description": "List all agents in the company with their roles and status.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
        },
        "list_tasks": {
            "func": list_tasks,
            "schema": {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List delegated tasks, optionally filtered by agent ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "agent_id": {
                                "type": "string",
                                "description": "Optional: filter tasks by agent ID",
                            },
                        },
                    },
                },
            },
        },
        "get_company_structure": {
            "func": get_company_structure,
            "schema": {
                "type": "function",
                "function": {
                    "name": "get_company_structure",
                    "description": "Get the company organizational structure with departments and roles.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
        },
        "list_departments": {
            "func": list_departments,
            "schema": {
                "type": "function",
                "function": {
                    "name": "list_departments",
                    "description": "List all departments and their roles.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
        },
    }
