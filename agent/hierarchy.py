"""Company hierarchy - departments, roles, and agent structure."""

import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()


class Role:
    """Represents a role in the company."""

    def __init__(
        self,
        name: str,
        department: str,
        description: str,
        permissions: list[str] | None = None,
        reports_to: str | None = None,
    ):
        self.name = name
        self.department = department
        self.description = description
        self.permissions = permissions or []
        self.reports_to = reports_to

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "department": self.department,
            "description": self.description,
            "permissions": self.permissions,
            "reports_to": self.reports_to,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Role":
        return cls(**data)


class Department:
    """Represents a department in the company."""

    def __init__(self, name: str, description: str, head: str | None = None):
        self.name = name
        self.description = description
        self.head = head  # Role name of department head
        self.roles: dict[str, Role] = {}

    def add_role(self, role: Role):
        """Add a role to the department."""
        self.roles[role.name] = role

    def remove_role(self, name: str):
        """Remove a role from the department."""
        if name in self.roles:
            del self.roles[name]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "head": self.head,
            "roles": {name: r.to_dict() for name, r in self.roles.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Department":
        dept = cls(
            name=data["name"],
            description=data["description"],
            head=data.get("head"),
        )
        for name, role_data in data.get("roles", {}).items():
            dept.add_role(Role.from_dict(role_data))
        return dept


class Hierarchy:
    """Manages the company structure."""

    def __init__(self, path: str = "hierarchy.json"):
        self.path = Path(path)
        self.departments: dict[str, Department] = {}
        self._load()

    def _load(self):
        """Load hierarchy from file."""
        if self.path.exists():
            try:
                with open(self.path) as f:
                    data = json.load(f)
                for name, dept_data in data.get("departments", {}).items():
                    self.departments[name] = Department.from_dict(dept_data)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load hierarchy: {e}[/yellow]")

    def _save(self):
        """Save hierarchy to file."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "departments": {
                    name: dept.to_dict()
                    for name, dept in self.departments.items()
                }
            }
            with open(self.path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[red]Error saving hierarchy: {e}[/red]")

    def add_department(self, name: str, description: str, head: str | None = None) -> Department:
        """Create a new department."""
        dept = Department(name=name, description=description, head=head)
        self.departments[name] = dept
        self._save()
        return dept

    def remove_department(self, name: str):
        """Remove a department."""
        if name in self.departments:
            del self.departments[name]
            self._save()

    def add_role(
        self,
        department: str,
        name: str,
        description: str,
        permissions: list[str] | None = None,
        reports_to: str | None = None,
    ) -> Role:
        """Add a role to a department."""
        if department not in self.departments:
            raise ValueError(f"Department not found: {department}")

        role = Role(
            name=name,
            department=department,
            description=description,
            permissions=permissions,
            reports_to=reports_to,
        )
        self.departments[department].add_role(role)
        self._save()
        return role

    def remove_role(self, department: str, name: str):
        """Remove a role from a department."""
        if department in self.departments:
            self.departments[department].remove_role(name)
            self._save()

    def get_role(self, department: str, name: str) -> Role | None:
        """Get a specific role."""
        if department in self.departments:
            return self.departments[department].roles.get(name)
        return None

    def get_all_roles(self) -> list[Role]:
        """Get all roles across all departments."""
        roles = []
        for dept in self.departments.values():
            roles.extend(dept.roles.values())
        return roles

    def get_subordinates(self, role_name: str) -> list[Role]:
        """Get all roles that report to the given role."""
        return [r for r in self.get_all_roles() if r.reports_to == role_name]

    def display(self):
        """Display the company structure as a table."""
        if not self.departments:
            console.print("[dim]No departments defined[/dim]")
            return

        table = Table(title="Company Structure")
        table.add_column("Department", style="cyan")
        table.add_column("Role", style="green")
        table.add_column("Description")
        table.add_column("Reports To", style="yellow")
        table.add_column("Permissions", style="dim")

        for dept_name, dept in self.departments.items():
            for role_name, role in dept.roles.items():
                table.add_row(
                    dept_name,
                    role_name,
                    role.description,
                    role.reports_to or "-",
                    ", ".join(role.permissions) if role.permissions else "-",
                )

        console.print(table)

    def to_system_prompt(self) -> str:
        """Generate system prompt section about the hierarchy."""
        if not self.departments:
            return ""

        lines = ["## Company Structure"]
        for dept_name, dept in self.departments.items():
            lines.append(f"\n### {dept_name}")
            lines.append(f"_{dept.description}_")
            if dept.head:
                lines.append(f"**Head:** {dept.head}")

            for role_name, role in dept.roles.items():
                lines.append(f"- **{role_name}**: {role.description}")
                if role.reports_to:
                    lines.append(f"  Reports to: {role.reports_to}")

        return "\n".join(lines)


# Default company structure
DEFAULT_STRUCTURE = {
    "Engineering": {
        "description": "Software development and technical operations",
        "head": "CTO",
        "roles": {
            "CTO": {
                "description": "Chief Technology Officer - oversees all technical decisions",
                "permissions": ["approve_architecture", "manage_team"],
                "reports_to": "CEO",
            },
            "Senior Developer": {
                "description": "Leads development of core features",
                "permissions": ["write_code", "review_code"],
                "reports_to": "CTO",
            },
            "Developer": {
                "description": "Implements features and fixes bugs",
                "permissions": ["write_code"],
                "reports_to": "Senior Developer",
            },
        },
    },
    "Product": {
        "description": "Product management and design",
        "head": "CPO",
        "roles": {
            "CPO": {
                "description": "Chief Product Officer - defines product vision",
                "permissions": ["approve_features", "manage_roadmap"],
                "reports_to": "CEO",
            },
            "Product Manager": {
                "description": "Manages product features and priorities",
                "permissions": ["define_requirements"],
                "reports_to": "CPO",
            },
        },
    },
    "Operations": {
        "description": "Business operations and administration",
        "head": "COO",
        "roles": {
            "COO": {
                "description": "Chief Operating Officer - manages daily operations",
                "permissions": ["manage_operations", "allocate_resources"],
                "reports_to": "CEO",
            },
        },
    },
}


def create_default_hierarchy(path: str = "hierarchy.json") -> Hierarchy:
    """Create a hierarchy with default company structure."""
    hierarchy = Hierarchy(path=path)

    if not hierarchy.departments:
        for dept_name, dept_data in DEFAULT_STRUCTURE.items():
            dept = hierarchy.add_department(
                name=dept_name,
                description=dept_data["description"],
                head=dept_data.get("head"),
            )
            for role_name, role_data in dept_data["roles"].items():
                hierarchy.add_role(
                    department=dept_name,
                    name=role_name,
                    description=role_data["description"],
                    permissions=role_data.get("permissions"),
                    reports_to=role_data.get("reports_to"),
                )

    return hierarchy
