"""Base platform interface."""

from abc import ABC, abstractmethod


class Platform(ABC):
    """Base class for messaging platforms."""

    @abstractmethod
    async def start(self):
        """Start the platform connection."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the platform connection."""
        pass

    @abstractmethod
    async def send_message(self, chat_id: str, text: str):
        """Send a message to a chat."""
        pass
