"""VPS management tools - full system access."""

import json
import os
import platform
import shutil
import subprocess
from typing import Optional

from rich.console import Console

console = Console()


def system_info() -> str:
    """Get comprehensive system information."""
    try:
        info = {
            "hostname": platform.node(),
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }

        # CPU info
        try:
            with open("/proc/cpuinfo") as f:
                cpu_info = f.read()
            info["cpu_cores"] = cpu_info.count("processor")
        except:
            pass

        # Memory info
        try:
            with open("/proc/meminfo") as f:
                mem_info = f.read()
            for line in mem_info.split("\n"):
                if "MemTotal" in line:
                    info["memory_total"] = line.split(":")[1].strip()
                elif "MemFree" in line:
                    info["memory_free"] = line.split(":")[1].strip()
                elif "MemAvailable" in line:
                    info["memory_available"] = line.split(":")[1].strip()
        except:
            pass

        # Disk info
        try:
            disk = shutil.disk_usage("/")
            info["disk_total"] = f"{disk.total // (1024**3)} GB"
            info["disk_used"] = f"{disk.used // (1024**3)} GB"
            info["disk_free"] = f"{disk.free // (1024**3)} GB"
            info["disk_percent"] = f"{disk.percent}%"
        except:
            pass

        return json.dumps(info, indent=2)

    except Exception as e:
        return f"Error: {e}"


def process_list(filter_name: Optional[str] = None) -> str:
    """List running processes."""
    try:
        cmd = "ps aux --sort=-%mem"
        if filter_name:
            cmd += f" | grep -i {filter_name}"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout[:5000] or "No processes found"
    except Exception as e:
        return f"Error: {e}"


def service_manage(service: str, action: str) -> str:
    """Manage systemd services (start, stop, restart, status, enable, disable)."""
    try:
        valid_actions = ["start", "stop", "restart", "status", "enable", "disable", "reload"]
        if action not in valid_actions:
            return f"Invalid action. Use: {', '.join(valid_actions)}"

        result = subprocess.run(
            f"systemctl {action} {service}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return json.dumps({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }, indent=2)

    except Exception as e:
        return f"Error: {e}"


def firewall_manage(action: str, port: Optional[int] = None, protocol: str = "tcp") -> str:
    """Manage UFW firewall rules."""
    try:
        if action == "status":
            cmd = "ufw status verbose"
        elif action == "allow" and port:
            cmd = f"ufw allow {port}/{protocol}"
        elif action == "deny" and port:
            cmd = f"ufw deny {port}/{protocol}"
        elif action == "delete" and port:
            cmd = f"ufw delete allow {port}/{protocol}"
        elif action == "enable":
            cmd = "ufw --force enable"
        elif action == "disable":
            cmd = "ufw disable"
        else:
            return "Invalid action or missing port"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr

    except Exception as e:
        return f"Error: {e}"


def user_manage(action: str, username: str, password: Optional[str] = None, groups: Optional[str] = None) -> str:
    """Manage system users."""
    try:
        if action == "add":
            cmd = f"useradd -m {username}"
            if password:
                subprocess.run(f"echo '{username}:{password}' | chpasswd", shell=True, capture_output=True)
            if groups:
                cmd = f"useradd -m -G {groups} {username}"
        elif action == "delete":
            cmd = f"userdel -r {username}"
        elif action == "lock":
            cmd = f"passwd -l {username}"
        elif action == "unlock":
            cmd = f"passwd -u {username}"
        elif action == "info":
            cmd = f"id {username} && finger {username} 2>/dev/null || cat /etc/passwd | grep {username}"
        else:
            return "Invalid action. Use: add, delete, lock, unlock, info"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr

    except Exception as e:
        return f"Error: {e}"


def cron_manage(action: str, schedule: Optional[str] = None, command: Optional[str] = None, user: str = "root") -> str:
    """Manage cron jobs."""
    try:
        if action == "list":
            result = subprocess.run(f"crontab -l -u {user}", shell=True, capture_output=True, text=True)
            return result.stdout or "No cron jobs"
        elif action == "add" and schedule and command:
            # Add to crontab
            result = subprocess.run(
                f"(crontab -l -u {user} 2>/dev/null; echo '{schedule} {command}') | crontab -u {user} -",
                shell=True, capture_output=True, text=True,
            )
            return f"Added cron job: {schedule} {command}"
        elif action == "clear":
            subprocess.run(f"crontab -r -u {user}", shell=True, capture_output=True)
            return "Cleared all cron jobs"
        else:
            return "Invalid action or missing parameters"

    except Exception as e:
        return f"Error: {e}"


def network_info() -> str:
    """Get network information."""
    try:
        info = {}

        # IP addresses
        result = subprocess.run("ip addr show", shell=True, capture_output=True, text=True)
        info["interfaces"] = result.stdout[:3000]

        # Public IP
        try:
            result = subprocess.run("curl -s ifconfig.me", shell=True, capture_output=True, text=True, timeout=5)
            info["public_ip"] = result.stdout.strip()
        except:
            pass

        # Listening ports
        result = subprocess.run("ss -tlnp", shell=True, capture_output=True, text=True)
        info["listening_ports"] = result.stdout[:2000]

        return json.dumps(info, indent=2)

    except Exception as e:
        return f"Error: {e}"


def install_package(package: str, manager: str = "auto") -> str:
    """Install a system package."""
    try:
        if manager == "auto":
            # Detect package manager
            if os.path.exists("/usr/bin/apt"):
                manager = "apt"
            elif os.path.exists("/usr/bin/yum"):
                manager = "yum"
            elif os.path.exists("/usr/bin/dnf"):
                manager = "dnf"
            elif os.path.exists("/usr/bin/pacman"):
                manager = "pacman"
            else:
                return "Could not detect package manager"

        commands = {
            "apt": f"apt-get update && apt-get install -y {package}",
            "yum": f"yum install -y {package}",
            "dnf": f"dnf install -y {package}",
            "pacman": f"pacman -S --noconfirm {package}",
            "pip": f"pip install {package}",
            "npm": f"npm install -g {package}",
        }

        cmd = commands.get(manager)
        if not cmd:
            return f"Unknown package manager: {manager}"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        return result.stdout[-2000:] + result.stderr[-1000:]

    except subprocess.TimeoutExpired:
        return "Installation timed out"
    except Exception as e:
        return f"Error: {e}"


def docker_manage(action: str, container: Optional[str] = None, image: Optional[str] = None, ports: Optional[str] = None) -> str:
    """Manage Docker containers."""
    try:
        if action == "ps":
            cmd = "docker ps -a"
        elif action == "images":
            cmd = "docker images"
        elif action == "run" and image:
            cmd = f"docker run -d"
            if ports:
                cmd += f" -p {ports}"
            cmd += f" {image}"
        elif action == "stop" and container:
            cmd = f"docker stop {container}"
        elif action == "start" and container:
            cmd = f"docker start {container}"
        elif action == "rm" and container:
            cmd = f"docker rm -f {container}"
        elif action == "logs" and container:
            cmd = f"docker logs --tail 100 {container}"
        elif action == "pull" and image:
            cmd = f"docker pull {image}"
        else:
            return "Invalid action or missing parameters"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.stdout[-5000:] + result.stderr[-2000:]

    except subprocess.TimeoutExpired:
        return "Docker command timed out"
    except Exception as e:
        return f"Error: {e}"


VPS_TOOLS = {
    "system_info": {
        "func": system_info,
        "schema": {
            "type": "function",
            "function": {
                "name": "system_info",
                "description": "Get comprehensive system information (OS, CPU, memory, disk).",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    },
    "process_list": {
        "func": process_list,
        "schema": {
            "type": "function",
            "function": {
                "name": "process_list",
                "description": "List running processes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filter_name": {"type": "string", "description": "Filter by process name"},
                    },
                },
            },
        },
    },
    "service_manage": {
        "func": service_manage,
        "schema": {
            "type": "function",
            "function": {
                "name": "service_manage",
                "description": "Manage systemd services (start, stop, restart, status, enable, disable).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service": {"type": "string", "description": "Service name"},
                        "action": {"type": "string", "description": "Action to perform", "enum": ["start", "stop", "restart", "status", "enable", "disable", "reload"]},
                    },
                    "required": ["service", "action"],
                },
            },
        },
    },
    "firewall_manage": {
        "func": firewall_manage,
        "schema": {
            "type": "function",
            "function": {
                "name": "firewall_manage",
                "description": "Manage UFW firewall rules.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action (status, allow, deny, delete, enable, disable)"},
                        "port": {"type": "integer", "description": "Port number"},
                        "protocol": {"type": "string", "description": "Protocol (tcp/udp)", "default": "tcp"},
                    },
                    "required": ["action"],
                },
            },
        },
    },
    "user_manage": {
        "func": user_manage,
        "schema": {
            "type": "function",
            "function": {
                "name": "user_manage",
                "description": "Manage system users (add, delete, lock, unlock, info).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to perform"},
                        "username": {"type": "string", "description": "Username"},
                        "password": {"type": "string", "description": "Password (for add action)"},
                        "groups": {"type": "string", "description": "Comma-separated groups (for add action)"},
                    },
                    "required": ["action", "username"],
                },
            },
        },
    },
    "cron_manage": {
        "func": cron_manage,
        "schema": {
            "type": "function",
            "function": {
                "name": "cron_manage",
                "description": "Manage cron jobs (list, add, clear).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action (list, add, clear)"},
                        "schedule": {"type": "string", "description": "Cron schedule (e.g., '0 2 * * *')"},
                        "command": {"type": "string", "description": "Command to run"},
                        "user": {"type": "string", "description": "System user (default: root)"},
                    },
                    "required": ["action"],
                },
            },
        },
    },
    "network_info": {
        "func": network_info,
        "schema": {
            "type": "function",
            "function": {
                "name": "network_info",
                "description": "Get network information (IPs, interfaces, listening ports).",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    },
    "install_package": {
        "func": install_package,
        "schema": {
            "type": "function",
            "function": {
                "name": "install_package",
                "description": "Install a system package using the appropriate package manager.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "package": {"type": "string", "description": "Package name"},
                        "manager": {"type": "string", "description": "Package manager (apt, yum, dnf, pacman, pip, npm)"},
                    },
                    "required": ["package"],
                },
            },
        },
    },
    "docker_manage": {
        "func": docker_manage,
        "schema": {
            "type": "function",
            "function": {
                "name": "docker_manage",
                "description": "Manage Docker containers (ps, run, stop, start, rm, logs, pull, images).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Docker action"},
                        "container": {"type": "string", "description": "Container name/ID"},
                        "image": {"type": "string", "description": "Docker image"},
                        "ports": {"type": "string", "description": "Port mappings (e.g., '8080:80')"},
                    },
                    "required": ["action"],
                },
            },
        },
    },
}
