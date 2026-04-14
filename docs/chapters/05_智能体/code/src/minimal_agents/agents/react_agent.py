from __future__ import annotations

from typing import Any, Dict, Optional

from ..core.agent_base import AgentBase
from ..core.llm import ToolCall


_REACT_PROMPT = """You are a ReAct-style assistant.
Use tools deliberately and finish with Finish(answer=...).
Use Thought(reasoning=...) when you need to reason explicitly.
"""


class ReActAgent(AgentBase):
    """ReAct loop with built-in Thought and Finish tools."""

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

    def _builtin_tools(self) -> list[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "Thought",
                    "description": "Record reasoning before action.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reasoning": {
                                "type": "string",
                                "description": "Your chain-of-thought summary for this step.",
                            }
                        },
                        "required": ["reasoning"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "Finish",
                    "description": "Return the final answer and stop.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "answer": {
                                "type": "string",
                                "description": "Final answer for the user.",
                            }
                        },
                        "required": ["answer"],
                    },
                },
            },
        ]

    def run(
        self,
        input_text: str,
        *,
        skill: Optional[str] = None,
        skill_args: Optional[str] = None,
        **kwargs,
    ) -> str:
        skill_context = self._resolve_skill_context(skill, skill_args)
        extra_system = _REACT_PROMPT
        if skill_context:
            extra_system = f"{_REACT_PROMPT}\n\nSkill context:\n{skill_context}"

        messages = self._build_messages(input_text, extra_system_prompt=extra_system)
        tools = self._builtin_tools() + self.tool_registry.to_openai_tools()

        final_answer = ""
        for _ in range(self.config.max_react_steps):
            llm_response = self.llm.complete(
                messages, tools=tools, tool_choice="auto", **kwargs
            )

            if not llm_response.tool_calls:
                if llm_response.content.strip():
                    final_answer = llm_response.content.strip()
                    break
                continue

            messages.append(
                {
                    "role": "assistant",
                    "content": llm_response.content or "",
                    "tool_calls": self._tool_calls_payload(llm_response.tool_calls),
                }
            )

            should_finish = False
            for call in llm_response.tool_calls:
                if call.name == "Thought":
                    reasoning = str(call.arguments.get("reasoning", "")).strip()
                    observation = (
                        f"Thought recorded: {reasoning}"
                        if reasoning
                        else "Thought recorded."
                    )
                elif call.name == "Finish":
                    final_answer = str(call.arguments.get("answer", "")).strip()
                    observation = "Final answer recorded."
                    should_finish = True
                else:
                    observation = self._execute_tool_call(call.name, call.arguments)

                messages.append(
                    {
                        "role": "tool",
                        "name": call.name,
                        "tool_call_id": call.id,
                        "content": observation,
                    }
                )

                if should_finish:
                    break

            if should_finish:
                break

        if not final_answer:
            fallback = self.llm.complete(messages, **kwargs)
            final_answer = fallback.content.strip()

        self._save_turn(input_text, final_answer)
        return final_answer
