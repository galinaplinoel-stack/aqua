"""Core chat engine - handles LLM interaction and conversation flow."""

from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from agent.persona import Persona

console = Console()


class ChatEngine:
    """Core chat engine with OpenAI-compatible API."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        persona: Persona,
    ):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.persona = persona
        self.messages: list[dict] = []
        self._init_system_prompt()

    def _init_system_prompt(self):
        """Set up system prompt from persona."""
        system_prompt = self.persona.system_prompt
        self.messages = [{"role": "system", "content": system_prompt}]

    def chat(self, user_input: str) -> str:
        """Send a message and get a response."""
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                stream=True,
            )

            # Stream the response
            full_response = ""
            with console.status("[dim]Thinking...[/dim]"):
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content

            # Print formatted response
            console.print()
            console.print(Panel(
                Markdown(full_response),
                title=f"[bold cyan]{self.persona.name}[/bold cyan]",
                border_style="cyan",
            ))
            console.print()

            # Save to history
            self.messages.append({"role": "assistant", "content": full_response})
            return full_response

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            # Remove the failed user message
            self.messages.pop()
            return ""

    def clear_history(self):
        """Clear conversation history, keep system prompt."""
        self._init_system_prompt()

    def get_history(self) -> list[dict]:
        """Get conversation history."""
        return self.messages.copy()
