from __future__ import annotations

from typing import Any, Dict, Optional

from ..core.agent_base import AgentBase
from ..core.llm import ToolCall


class MinimalAgent(AgentBase):
    """Smallest useful agent loop: model -> tool calls -> model."""

    def _tool_calls_payload(self, calls: list[ToolCall]) -> list[Dict[str, Any]]:
        payload: list[Dict[str, Any]] = []
        for call in calls:
            payload.append(
                {
                    "id": call.id,
                    "type": "function",
                    "function": {"name": call.name, "arguments": call.arguments},
                }
            )
        return payload

    def run(
        self,
        input_text: str,
        *,
        skill: Optional[str] = None,
        skill_args: Optional[str] = None,
        **kwargs,
    ) -> str:
        skill_context = self._resolve_skill_context(skill, skill_args)
        messages = self._build_messages(input_text, extra_system_prompt=skill_context)
        tools = self.tool_registry.to_openai_tools()

        if not tools:
            result = self.llm.complete(messages, **kwargs)
            final = result.content.strip() or ""
            self._save_turn(input_text, final)
            return final

        final_answer = ""
        for _ in range(self.config.max_tool_iterations):
            llm_response = self.llm.complete(messages, tools=tools, tool_choice="auto", **kwargs)

            if not llm_response.tool_calls:
                final_answer = llm_response.content.strip() or final_answer
                break

            messages.append(
                {
                    "role": "assistant",
                    "content": llm_response.content or "",
                    "tool_calls": self._tool_calls_payload(llm_response.tool_calls),
                }
            )

            for call in llm_response.tool_calls:
                tool_result = self._execute_tool_call(call.name, call.arguments)
                messages.append(
                    {
                        "role": "tool",
                        "name": call.name,
                        "tool_call_id": call.id,
                        "content": tool_result,
                    }
                )

        if not final_answer:
            fallback = self.llm.complete(messages, **kwargs)
            final_answer = fallback.content.strip()

        self._save_turn(input_text, final_answer)
        return final_answer
