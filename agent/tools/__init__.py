"""AQUA Tools - Comprehensive tool collection."""

from agent.tools.web import WEB_SEARCH_TOOLS
from agent.tools.http import HTTP_TOOLS
from agent.tools.code_exec import CODE_EXEC_TOOLS
from agent.tools.git import GIT_TOOLS
from agent.tools.database import DATABASE_TOOLS
from agent.tools.file_formats import FILE_FORMAT_TOOLS
from agent.tools.email import EMAIL_TOOLS
from agent.tools.vps import VPS_TOOLS
from agent.tools.monitoring import MONITORING_TOOLS
from agent.tools.caching import CACHING_TOOLS
from agent.tools.workflow import WORKFLOW_TOOLS
from agent.tools.notifications import NOTIFICATION_TOOLS
from agent.tools.calendar import CALENDAR_TOOLS
from agent.tools.plugins import PLUGIN_TOOLS
from agent.tools.auth import AUTH_TOOLS
from agent.tools.vector_memory import VECTOR_MEMORY_TOOLS


# All tool categories
ALL_TOOL_CATEGORIES = {
    "web": WEB_SEARCH_TOOLS,
    "http": HTTP_TOOLS,
    "code_exec": CODE_EXEC_TOOLS,
    "git": GIT_TOOLS,
    "database": DATABASE_TOOLS,
    "file_formats": FILE_FORMAT_TOOLS,
    "email": EMAIL_TOOLS,
    "vps": VPS_TOOLS,
    "monitoring": MONITORING_TOOLS,
    "caching": CACHING_TOOLS,
    "workflow": WORKFLOW_TOOLS,
    "notifications": NOTIFICATION_TOOLS,
    "calendar": CALENDAR_TOOLS,
    "plugins": PLUGIN_TOOLS,
    "auth": AUTH_TOOLS,
    "vector_memory": VECTOR_MEMORY_TOOLS,
}


def get_all_tools() -> dict:
    """Get all tools merged into one dict."""
    all_tools = {}
    for category_tools in ALL_TOOL_CATEGORIES.values():
        all_tools.update(category_tools)
    return all_tools


def get_tools_by_category(category: str) -> dict:
    """Get tools for a specific category."""
    return ALL_TOOL_CATEGORIES.get(category, {})
