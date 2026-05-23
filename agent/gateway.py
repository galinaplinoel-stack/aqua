"""Gateway - manages platform connections and chat sessions."""

import asyncio
from typing import Any

from rich.console import Console

from agent.core import ChatEngine
from agent.memory import Memory
from agent.persona import Persona
from agent.tools import ToolRegistry

console = Console()


class Gateway:
    """Manages multiple platform connections and chat sessions."""

    def __init__(
        self,
        config: dict,
        persona: Persona,
        tools: ToolRegistry | None = None,
        memory: Memory | None = None,
    ):
        self.config = config
        self.persona = persona
        self.tools = tools
        self.memory = memory
        self.sessions: dict[str, ChatEngine] = {}
        self.platforms = []

    def get_session(self, chat_id: str) -> ChatEngine:
        """Get or create a chat session for a chat ID."""
        if chat_id not in self.sessions:
            self.sessions[chat_id] = ChatEngine(
                base_url=self.config["provider"]["base_url"],
                api_key=self.config["provider"]["api_key"],
                model=self.config["provider"]["model"],
                persona=self.persona,
                tools=self.tools,
                memory=self.memory,
            )
        return self.sessions[chat_id]

    async def handle_message(self, chat_id: str, message: str) -> str:
        """Handle an incoming message from any platform."""
        engine = self.get_session(chat_id)

        # Handle clear command
        if message.strip().lower() == "/clear":
            engine.clear_history()
            return "History cleared."

        # Normal chat
        response = engine.chat(message)
        return response

    async def start_platforms(self):
        """Start all configured platforms."""
        platforms_config = self.config.get("platforms", {})

        # Telegram
        if "telegram" in platforms_config:
            from agent.platforms.telegram import TelegramPlatform

            tg_config = platforms_config["telegram"]
            telegram = TelegramPlatform(
                token=tg_config["token"],
                chat_handler=self.handle_message,
                allowed_chat_ids=tg_config.get("allowed_chat_ids"),
            )
            self.platforms.append(telegram)
            console.print("[green]Starting Telegram bot...[/green]")
            await telegram.start()

    async def stop_platforms(self):
        """Stop all platforms."""
        for platform in self.platforms:
            await platform.stop()
