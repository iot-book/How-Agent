from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .config import AgentConfig
from .llm import HelloAgentsLLM
from .message import Message
from ..tools.registry import ToolRegistry


class AgentBase(ABC):
    """Shared runtime utilities for all teaching agents."""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        *,
        system_prompt: Optional[str] = None,
        tool_registry: Optional[ToolRegistry] = None,
        config: Optional[AgentConfig] = None,
        skill_resolver: Optional["SkillResolver"] = None,
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt or "You are a helpful assistant."
        self.tool_registry = tool_registry or ToolRegistry()
        self.config = config or AgentConfig()
        self.skill_resolver = skill_resolver
        self.history: list[Message] = []

    def _build_messages(
        self,
        user_input: str,
        *,
        extra_system_prompt: Optional[str] = None,
    ) -> list[dict]:
        messages: list[dict] = []

        system_chunks = [self.system_prompt.strip()] if self.system_prompt else []
        if extra_system_prompt:
            system_chunks.append(extra_system_prompt.strip())
        if system_chunks:
            messages.append({"role": "system", "content": "\n\n".join(system_chunks)})

        for message in self.history[-self.config.max_history_messages :]:
            messages.append(message.to_dict())

        messages.append({"role": "user", "content": user_input})
        return messages

    def _resolve_skill_context(
        self, skill: Optional[str], skill_args: Optional[str]
    ) -> Optional[str]:
        if not skill or self.skill_resolver is None:
            return None
        return self.skill_resolver.render(skill, skill_args or "")

    def _execute_tool_call(self, tool_name: str, arguments: dict) -> str:
        response = self.tool_registry.execute_tool(tool_name, arguments)
        return response.to_message()

    def _save_turn(self, user_input: str, assistant_output: str) -> None:
        self.history.append(Message(role="user", content=user_input))
        self.history.append(Message(role="assistant", content=assistant_output))

    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        ...


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..skills.resolver import SkillResolver
