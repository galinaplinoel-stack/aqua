"""Persona management - loads Aqua.md as system prompt."""

from pathlib import Path


class Persona:
    """Manages the agent's persona by loading from Aqua.md."""

    def __init__(self, name: str = "AQUA", persona_path: str = "Aqua.md"):
        self.name = name
        self.persona_path = Path(persona_path)
        self._system_prompt = None

    def load(self) -> str:
        """Load persona from Aqua.md file."""
        if self._system_prompt is not None:
            return self._system_prompt

        if self.persona_path.exists():
            content = self.persona_path.read_text(encoding="utf-8")
            # Strip HTML comments (instructions for user)
            import re
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            # Strip empty lines at start/end
            content = content.strip()
            self._system_prompt = content
        else:
            self._system_prompt = f"You are {self.name}, a helpful AI assistant."

        return self._system_prompt

    def reload(self) -> str:
        """Force reload persona from file."""
        self._system_prompt = None
        return self.load()

    @property
    def system_prompt(self) -> str:
        """Get the system prompt, loading if needed."""
        return self.load()
