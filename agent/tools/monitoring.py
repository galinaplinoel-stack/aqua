"""Monitoring and health check tools."""

import json
import os
import platform
import subprocess
import time
from typing import Optional

from rich.console import Console

console = Console()


def health_check() -> str:
    """Comprehensive system health check."""
    try:
        health = {
            "timestamp": time.time(),
            "status": "healthy",
            "checks": {}
        }

        # CPU check
        try:
            load = os.getloadavg()
            cpu_count = os.cpu_count() or 1
            cpu_percent = (load[0] / cpu_count) * 100
            health["checks"]["cpu"] = {
                "load_1m": load[0],
                "load_5m": load[1],
                "load_15m": load[2],
                "percent": round(cpu_percent, 1),
                "status": "critical" if cpu_percent > 90 else "warning" if cpu_percent > 70 else "ok"
            }
        except:
            pass

        # Memory check
        try:
            with open("/proc/meminfo") as f:
                mem_info = f.read()
            mem = {}
            for line in mem_info.split("\n"):
                if ":" in line:
                    key, val = line.split(":")
                    mem[key.strip()] = int(val.strip().split()[0])

            total = mem.get("MemTotal", 0)
            available = mem.get("MemAvailable", 0)
            used_percent = ((total - available) / total * 100) if total > 0 else 0

            health["checks"]["memory"] = {
                "total_mb": round(total / 1024),
                "available_mb": round(available / 1024),
                "used_percent": round(used_percent, 1),
                "status": "critical" if used_percent > 90 else "warning" if used_percent > 80 else "ok"
            }
        except:
            pass

        # Disk check
        try:
            disk = os.statvfs("/")
            total = disk.f_blocks * disk.f_frsize
            free = disk.f_bfree * disk.f_frsize
            used_percent = ((total - free) / total * 100) if total > 0 else 0

            health["checks"]["disk"] = {
                "total_gb": round(total / (1024**3), 1),
                "free_gb": round(free / (1024**3), 1),
                "used_percent": round(used_percent, 1),
                "status": "critical" if used_percent > 95 else "warning" if used_percent > 85 else "ok"
            }
        except:
            pass

        # Check critical services
        critical_services = ["ssh", "nginx", "docker"]
        for svc in critical_services:
            try:
                result = subprocess.run(
                    f"systemctl is-active {svc}",
                    shell=True, capture_output=True, text=True
                )
                if result.returncode == 0:
                    health["checks"][f"service_{svc}"] = {"status": "ok"}
            except:
                pass

        # Overall status
        statuses = [c.get("status", "ok") for c in health["checks"].values()]
        if "critical" in statuses:
            health["status"] = "critical"
        elif "warning" in statuses:
            health["status"] = "warning"

        return json.dumps(health, indent=2)

    except Exception as e:
        return f"Error: {e}"


def disk_usage(path: str = "/") -> str:
    """Get disk usage for a path."""
    try:
        result = subprocess.run(f"df -h {path}", shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def memory_usage() -> str:
    """Get memory usage details."""
    try:
        result = subprocess.run("free -h", shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def top_processes(sort: str = "mem", count: int = 10) -> str:
    """Get top processes by CPU or memory usage."""
    try:
        if sort == "cpu":
            cmd = f"ps aux --sort=-%cpu | head -{count + 1}"
        else:
            cmd = f"ps aux --sort=-%mem | head -{count + 1}"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def check_port(host: str, port: int) -> str:
    """Check if a port is open."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()

        return json.dumps({
            "host": host,
            "port": port,
            "open": result == 0,
            "status": "open" if result == 0 else "closed",
        })
    except Exception as e:
        return f"Error: {e}"


MONITORING_TOOLS = {
    "health_check": {
        "func": health_check,
        "schema": {
            "type": "function",
            "function": {
                "name": "health_check",
                "description": "Comprehensive system health check (CPU, memory, disk, services).",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    },
    "disk_usage": {
        "func": disk_usage,
        "schema": {
            "type": "function",
            "function": {
                "name": "disk_usage",
                "description": "Get disk usage for a path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to check (default: /)"},
                    },
                },
            },
        },
    },
    "memory_usage": {
        "func": memory_usage,
        "schema": {
            "type": "function",
            "function": {
                "name": "memory_usage",
                "description": "Get memory usage details.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    },
    "top_processes": {
        "func": top_processes,
        "schema": {
            "type": "function",
            "function": {
                "name": "top_processes",
                "description": "Get top processes by CPU or memory usage.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sort": {"type": "string", "description": "Sort by 'cpu' or 'mem' (default: mem)"},
                        "count": {"type": "integer", "description": "Number of processes (default: 10)"},
                    },
                },
            },
        },
    },
    "check_port": {
        "func": check_port,
        "schema": {
            "type": "function",
            "function": {
                "name": "check_port",
                "description": "Check if a port is open on a host.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string", "description": "Host to check"},
                        "port": {"type": "integer", "description": "Port number"},
                    },
                    "required": ["host", "port"],
                },
            },
        },
    },
}
