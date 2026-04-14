from __future__ import annotations

import json
import re
from typing import Optional

from ..core.agent_base import AgentBase
from .minimal_agent import MinimalAgent


_PLANNER_PROMPT = """You are a planning assistant.
Return a compact plan as JSON: {"steps": ["step 1", "step 2"]}.
"""

_EXECUTOR_PROMPT = """You are an execution assistant.
Solve the current step using available tools when needed.
"""


class PlanAndExecuteAgent(AgentBase):
    """Two-phase agent: plan first, then execute each step."""

    def __init__(
        self,
        name,
        llm,
        *,
        system_prompt=None,
        tool_registry=None,
        config=None,
        skill_resolver=None,
        planner_prompt: Optional[str] = None,
        executor_prompt: Optional[str] = None,
    ):
        super().__init__(
            name,
            llm,
            system_prompt=system_prompt,
            tool_registry=tool_registry,
            config=config,
            skill_resolver=skill_resolver,
        )
        self.planner_prompt = planner_prompt or _PLANNER_PROMPT
        self.executor_prompt = executor_prompt or _EXECUTOR_PROMPT

    def _parse_plan(self, text: str) -> list[str]:
        stripped = text.strip()
        if not stripped:
            return []

        try:
            payload = json.loads(stripped)
            if isinstance(payload, dict) and isinstance(payload.get("steps"), list):
                return [
                    str(step).strip() for step in payload["steps"] if str(step).strip()
                ]
            if isinstance(payload, list):
                return [str(step).strip() for step in payload if str(step).strip()]
        except json.JSONDecodeError:
            pass

        steps: list[str] = []
        for line in stripped.splitlines():
            cleaned = re.sub(r"^\s*\d+[\).:-]?\s*", "", line).strip()
            if cleaned:
                steps.append(cleaned)
        return steps

    def _create_plan(self, question: str, **kwargs) -> list[str]:
        planning_messages = [
            {"role": "system", "content": self.planner_prompt},
            {"role": "user", "content": question},
        ]
        response = self.llm.complete(planning_messages, **kwargs)
        steps = self._parse_plan(response.content)
        return steps or [question]

    def run(
        self,
        input_text: str,
        *,
        skill: Optional[str] = None,
        skill_args: Optional[str] = None,
        **kwargs,
    ) -> str:
        plan = self._create_plan(input_text, **kwargs)[: self.config.plan_max_steps]

        execution_log: list[tuple[str, str]] = []
        for index, step in enumerate(plan, start=1):
            previous = "\n".join(
                f"{i}. {s} => {r}" for i, (s, r) in enumerate(execution_log, start=1)
            ) or "None"

            step_prompt = (
                f"Task: {input_text}\n"
                f"Current step ({index}/{len(plan)}): {step}\n"
                f"Previous results:\n{previous}"
            )

            executor = MinimalAgent(
                name=f"{self.name}-executor",
                llm=self.llm,
                system_prompt=self.executor_prompt,
                tool_registry=self.tool_registry,
                config=self.config,
                skill_resolver=self.skill_resolver,
            )
            step_result = executor.run(
                step_prompt,
                skill=skill if index == 1 else None,
                skill_args=skill_args if index == 1 else None,
                **kwargs,
            )
            execution_log.append((step, step_result))

        summary_messages = [
            {
                "role": "system",
                "content": "Summarize step execution into one concise final answer.",
            },
            {
                "role": "user",
                "content": "\n".join(
                    [f"Original task: {input_text}"]
                    + [f"- {step}: {result}" for step, result in execution_log]
                ),
            },
        ]

        summary = self.llm.complete(summary_messages, **kwargs).content.strip()
        final_answer = summary or (execution_log[-1][1] if execution_log else "")
        self._save_turn(input_text, final_answer)
        return final_answer
