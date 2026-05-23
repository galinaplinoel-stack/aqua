"""Code execution tools - run Python, shell, and scripts."""

import json
import os
import subprocess
import sys
import tempfile
from typing import Optional

from rich.console import Console

console = Console()


def run_python(code: str, timeout: int = 30) -> str:
    """Execute Python code and return output."""
    try:
        # Write code to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

            return json.dumps(output, indent=2)

        finally:
            os.unlink(temp_path)

    except subprocess.TimeoutExpired:
        return f"Error: Code execution timed out ({timeout}s)"
    except Exception as e:
        return f"Error: {e}"


def run_shell(command: str, timeout: int = 60, cwd: Optional[str] = None) -> str:
    """Execute shell command with full access."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )

        output = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

        return json.dumps(output, indent=2)

    except subprocess.TimeoutExpired:
        return f"Error: Command timed out ({timeout}s)"
    except Exception as e:
        return f"Error: {e}"


def run_script(script_path: str, args: Optional[str] = None, timeout: int = 60) -> str:
    """Execute a script file."""
    try:
        if not os.path.exists(script_path):
            return f"Error: Script not found: {script_path}"

        # Determine interpreter
        if script_path.endswith(".py"):
            cmd = [sys.executable, script_path]
        elif script_path.endswith(".sh") or script_path.endswith(".bash"):
            cmd = ["bash", script_path]
        elif script_path.endswith(".js"):
            cmd = ["node", script_path]
        else:
            cmd = [script_path]

        if args:
            cmd.extend(args.split())

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

        return json.dumps(output, indent=2)

    except subprocess.TimeoutExpired:
        return f"Error: Script timed out ({timeout}s)"
    except Exception as e:
        return f"Error: {e}"


CODE_EXEC_TOOLS = {
    "run_python": {
        "func": run_python,
        "schema": {
            "type": "function",
            "function": {
                "name": "run_python",
                "description": "Execute Python code and return stdout/stderr. Use for calculations, data processing, testing code.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Python code to execute"},
                        "timeout": {"type": "integer", "description": "Timeout in seconds (default: 30)"},
                    },
                    "required": ["code"],
                },
            },
        },
    },
    "run_shell": {
        "func": run_shell,
        "schema": {
            "type": "function",
            "function": {
                "name": "run_shell",
                "description": "Execute shell command with full system access. Use for system operations, file management, installations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command to execute"},
                        "timeout": {"type": "integer", "description": "Timeout in seconds (default: 60)"},
                        "cwd": {"type": "string", "description": "Working directory"},
                    },
                    "required": ["command"],
                },
            },
        },
    },
    "run_script": {
        "func": run_script,
        "schema": {
            "type": "function",
            "function": {
                "name": "run_script",
                "description": "Execute a script file (Python, Bash, Node.js).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "script_path": {"type": "string", "description": "Path to script file"},
                        "args": {"type": "string", "description": "Arguments to pass to script"},
                        "timeout": {"type": "integer", "description": "Timeout in seconds (default: 60)"},
                    },
                    "required": ["script_path"],
                },
            },
        },
    },
}
