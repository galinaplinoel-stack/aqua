"""Notification system tools."""

import json
import subprocess
from typing import Optional

import requests
from rich.console import Console

console = Console()


def send_discord_webhook(webhook_url: str, message: str, username: str = "AQUA") -> str:
    """Send a message via Discord webhook."""
    try:
        data = {
            "content": message,
            "username": username,
        }
        response = requests.post(webhook_url, json=data, timeout=10)
        if response.status_code == 204:
            return "Discord notification sent"
        return f"Discord error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"


def send_slack_webhook(webhook_url: str, message: str, channel: Optional[str] = None) -> str:
    """Send a message via Slack webhook."""
    try:
        data = {"text": message}
        if channel:
            data["channel"] = channel
        response = requests.post(webhook_url, json=data, timeout=10)
        if response.status_code == 200:
            return "Slack notification sent"
        return f"Slack error: {response.text}"
    except Exception as e:
        return f"Error: {e}"


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> str:
    """Send a message via Telegram bot."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            return "Telegram notification sent"
        return f"Telegram error: {response.text}"
    except Exception as e:
        return f"Error: {e}"


def send_ntfy(topic: str, message: str, title: str = "AQUA", priority: str = "default") -> str:
    """Send a notification via ntfy.sh."""
    try:
        url = f"https://ntfy.sh/{topic}"
        headers = {
            "Title": title,
            "Priority": priority,
        }
        response = requests.post(url, data=message, headers=headers, timeout=10)
        if response.status_code == 200:
            return f"ntfy notification sent to {topic}"
        return f"ntfy error: {response.text}"
    except Exception as e:
        return f"Error: {e}"


def send_email_notification(smtp_host: str, smtp_port: int, username: str, password: str, to: str, subject: str, message: str) -> str:
    """Send email notification."""
    try:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = username
        msg["To"] = to

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, [to], msg.as_string())

        return "Email notification sent"
    except Exception as e:
        return f"Error: {e}"


NOTIFICATION_TOOLS = {
    "send_discord_webhook": {
        "func": send_discord_webhook,
        "schema": {
            "type": "function",
            "function": {
                "name": "send_discord_webhook",
                "description": "Send a message via Discord webhook.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "webhook_url": {"type": "string", "description": "Discord webhook URL"},
                        "message": {"type": "string", "description": "Message to send"},
                        "username": {"type": "string", "description": "Bot username (default: AQUA)"},
                    },
                    "required": ["webhook_url", "message"],
                },
            },
        },
    },
    "send_slack_webhook": {
        "func": send_slack_webhook,
        "schema": {
            "type": "function",
            "function": {
                "name": "send_slack_webhook",
                "description": "Send a message via Slack webhook.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "webhook_url": {"type": "string", "description": "Slack webhook URL"},
                        "message": {"type": "string", "description": "Message to send"},
                        "channel": {"type": "string", "description": "Channel to post in"},
                    },
                    "required": ["webhook_url", "message"],
                },
            },
        },
    },
    "send_telegram_message": {
        "func": send_telegram_message,
        "schema": {
            "type": "function",
            "function": {
                "name": "send_telegram_message",
                "description": "Send a message via Telegram bot.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bot_token": {"type": "string", "description": "Telegram bot token"},
                        "chat_id": {"type": "string", "description": "Chat ID to send to"},
                        "message": {"type": "string", "description": "Message to send"},
                    },
                    "required": ["bot_token", "chat_id", "message"],
                },
            },
        },
    },
    "send_ntfy": {
        "func": send_ntfy,
        "schema": {
            "type": "function",
            "function": {
                "name": "send_ntfy",
                "description": "Send a notification via ntfy.sh (push notifications).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "ntfy topic/channel"},
                        "message": {"type": "string", "description": "Notification message"},
                        "title": {"type": "string", "description": "Notification title"},
                        "priority": {"type": "string", "description": "Priority (min, low, default, high, urgent)"},
                    },
                    "required": ["topic", "message"],
                },
            },
        },
    },
}
