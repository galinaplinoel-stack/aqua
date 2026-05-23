"""Git integration tools."""

import json
import subprocess
from typing import Optional

from rich.console import Console

console = Console()


def git_command(command: str, cwd: Optional[str] = None) -> str:
    """Execute a git command."""
    try:
        result = subprocess.run(
            f"git {command}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd,
        )

        output = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

        return json.dumps(output, indent=2)

    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except Exception as e:
        return f"Error: {e}"


def git_clone(url: str, path: Optional[str] = None) -> str:
    """Clone a git repository."""
    cmd = f"clone {url}"
    if path:
        cmd += f" {path}"
    return git_command(cmd)


def git_status(cwd: Optional[str] = None) -> str:
    """Get git status."""
    return git_command("status", cwd=cwd)


def git_log(count: int = 10, cwd: Optional[str] = None) -> str:
    """Get git log."""
    return git_command(f"log --oneline -{count}", cwd=cwd)


def git_diff(file: Optional[str] = None, cwd: Optional[str] = None) -> str:
    """Get git diff."""
    cmd = "diff"
    if file:
        cmd += f" {file}"
    return git_command(cmd, cwd=cwd)


def git_commit(message: str, cwd: Optional[str] = None) -> str:
    """Stage all changes and commit."""
    git_command("add -A", cwd=cwd)
    return git_command(f'commit -m "{message}"', cwd=cwd)


def git_push(remote: str = "origin", branch: str = "main", cwd: Optional[str] = None) -> str:
    """Push changes to remote."""
    return git_command(f"push {remote} {branch}", cwd=cwd)


def git_pull(remote: str = "origin", branch: str = "main", cwd: Optional[str] = None) -> str:
    """Pull changes from remote."""
    return git_command(f"pull {remote} {branch}", cwd=cwd)


GIT_TOOLS = {
    "git_clone": {
        "func": git_clone,
        "schema": {
            "type": "function",
            "function": {
                "name": "git_clone",
                "description": "Clone a git repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Repository URL"},
                        "path": {"type": "string", "description": "Local path to clone into"},
                    },
                    "required": ["url"],
                },
            },
        },
    },
    "git_status": {
        "func": git_status,
        "schema": {
            "type": "function",
            "function": {
                "name": "git_status",
                "description": "Get git repository status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cwd": {"type": "string", "description": "Repository directory"},
                    },
                },
            },
        },
    },
    "git_log": {
        "func": git_log,
        "schema": {
            "type": "function",
            "function": {
                "name": "git_log",
                "description": "Get git commit history.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "description": "Number of commits to show (default: 10)"},
                        "cwd": {"type": "string", "description": "Repository directory"},
                    },
                },
            },
        },
    },
    "git_commit": {
        "func": git_commit,
        "schema": {
            "type": "function",
            "function": {
                "name": "git_commit",
                "description": "Stage all changes and commit.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Commit message"},
                        "cwd": {"type": "string", "description": "Repository directory"},
                    },
                    "required": ["message"],
                },
            },
        },
    },
    "git_push": {
        "func": git_push,
        "schema": {
            "type": "function",
            "function": {
                "name": "git_push",
                "description": "Push changes to remote repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "remote": {"type": "string", "description": "Remote name (default: origin)"},
                        "branch": {"type": "string", "description": "Branch name (default: main)"},
                        "cwd": {"type": "string", "description": "Repository directory"},
                    },
                },
            },
        },
    },
    "git_pull": {
        "func": git_pull,
        "schema": {
            "type": "function",
            "function": {
                "name": "git_pull",
                "description": "Pull changes from remote repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "remote": {"type": "string", "description": "Remote name (default: origin)"},
                        "branch": {"type": "string", "description": "Branch name (default: main)"},
                        "cwd": {"type": "string", "description": "Repository directory"},
                    },
                },
            },
        },
    },
}
