"""Telegram platform integration."""

import asyncio
from typing import Callable

from rich.console import Console

from agent.platforms import Platform

console = Console()


class TelegramPlatform(Platform):
    """Telegram bot platform using python-telegram-bot."""

    def __init__(
        self,
        token: str,
        chat_handler: Callable,
        allowed_chat_ids: list[str] | None = None,
    ):
        self.token = token
        self.chat_handler = chat_handler
        self.allowed_chat_ids = allowed_chat_ids
        self.app = None

    async def start(self):
        """Start the Telegram bot."""
        try:
            from telegram import Update
            from telegram.ext import (
                Application,
                CommandHandler,
                ContextTypes,
                MessageHandler,
                filters,
            )
        except ImportError:
            console.print("[red]python-telegram-bot not installed. Run: pip install python-telegram-bot[/red]")
            return

        async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Handle incoming messages."""
            if not update.message or not update.message.text:
                return

            chat_id = str(update.message.chat_id)

            # Check allowed chats
            if self.allowed_chat_ids and chat_id not in self.allowed_chat_ids:
                return

            user_input = update.message.text

            # Handle commands
            if user_input.startswith("/"):
                cmd = user_input.split()[0].lower()
                if cmd == "/start":
                    await update.message.reply_text(
                        "🤖 AQUA is ready! Send me a message."
                    )
                    return
                elif cmd == "/help":
                    await update.message.reply_text(
                        "/start — Start bot\n"
                        "/help  — Show help\n"
                        "/clear — Clear history\n"
                        "\nOr just send a message to chat!"
                    )
                    return

            # Process through chat handler
            response = await self.chat_handler(chat_id, user_input)
            if response:
                await update.message.reply_text(response)

        # Build application
        self.app = Application.builder().token(self.token).build()
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        ))

        console.print("[green]Telegram bot started[/green]")
        self.app.run_polling(drop_pending_updates=True)

    async def stop(self):
        """Stop the Telegram bot."""
        if self.app:
            await self.app.stop()

    async def send_message(self, chat_id: str, text: str):
        """Send a message to a Telegram chat."""
        if self.app:
            await self.app.bot.send_message(chat_id=chat_id, text=text)
