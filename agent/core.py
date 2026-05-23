"""Core chat engine - handles LLM interaction and conversation flow."""

from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from agent.persona import Persona
from agent.tools import ToolRegistry

console = Console()


class ChatEngine:
    """Core chat engine with OpenAI-compatible API and tool support."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        persona: Persona,
        tools: ToolRegistry | None = None,
    ):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.persona = persona
        self.tools = tools
        self.messages: list[dict] = []
        self._init_system_prompt()

    def _init_system_prompt(self):
        """Set up system prompt from persona."""
        system_prompt = self.persona.system_prompt
        self.messages = [{"role": "system", "content": system_prompt}]

    def _get_tools_param(self) -> list[dict] | None:
        """Get tools parameter for API call."""
        if self.tools and self.tools.tools:
            return self.tools.get_schemas()
        return None

    def chat(self, user_input: str) -> str:
        """Send a message and get a response."""
        self.messages.append({"role": "user", "content": user_input})
        return self._run_conversation()

    def _run_conversation(self) -> str:
        """Run the conversation loop, handling tool calls."""
        try:
            tools_param = self._get_tools_param()
            kwargs = {"model": self.model, "messages": self.messages}
            if tools_param:
                kwargs["tools"] = tools_param

            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message

            # Handle tool calls
            if message.tool_calls:
                # Append assistant message with tool calls
                self.messages.append(message.model_dump())

                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = tool_call.function.arguments

                    if self.tools:
                        console.print(f"  [dim]🔧 Calling: {func_name}[/dim]")
                        result = self.tools.execute(func_name, func_args)
                    else:
                        result = "Error: Tools not available"

                    # Append tool result
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })

                # Continue conversation after tool execution
                return self._run_conversation()

            # Regular response (no tool calls)
            full_response = message.content or ""

            console.print()
            console.print(Panel(
                Markdown(full_response),
                title=f"[bold cyan]{self.persona.name}[/bold cyan]",
                border_style="cyan",
            ))
            console.print()

            self.messages.append({"role": "assistant", "content": full_response})
            return full_response

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            # Remove the failed user message
            if self.messages and self.messages[-1]["role"] == "user":
                self.messages.pop()
            return ""

    def clear_history(self):
        """Clear conversation history, keep system prompt."""
        self._init_system_prompt()

    def get_history(self) -> list[dict]:
        """Get conversation history."""
        return self.messages.copy()
