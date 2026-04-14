"""Fill-in-the-blank exercise for the Agent chapter.

Goal:
1. design a custom agent loop that is different from ReAct
2. create a checklist
3. execute each checklist item
4. review each result
5. retry once when review fails
6. summarize the final answer
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Any, Optional


def bootstrap() -> None:
    project_root = Path(__file__).resolve().parents[3]
    src_path = project_root / "src"
    src_str = str(src_path)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


bootstrap()

from minimal_agents import HelloAgentsLLM, MinimalAgent, ScriptedLLMBackend, ToolRegistry
from minimal_agents.core.agent_base import AgentBase


NOTE_PATH = Path(__file__).resolve().parent / "sample_lesson_note.md"


@dataclass
class StepResult:
    item: str
    result: str
    passed: bool
    feedback: str
    retried: bool = False


def read_markdown(path: str) -> dict[str, Any]:
    """Read a UTF-8 Markdown file."""
    markdown_path = Path(path)
    if not markdown_path.exists():
        return {"path": path, "error": "file not found"}
    return {"path": path, "content": markdown_path.read_text(encoding="utf-8")}


def build_tool_registry() -> ToolRegistry:
    """Build tools used by the homework agent.

    Tool registration was already practiced in chapter 3, so it is provided here.
    """
    registry = ToolRegistry()
    registry.register_function(read_markdown, "Read UTF-8 content from a Markdown file.")
    return registry


def parse_checklist_items(text: str) -> list[str]:
    """Parse {"items": [...]} from a model response."""
    payload = json.loads(text)
    items = payload.get("items", [])
    if not isinstance(items, list):
        return []
    return [str(item).strip() for item in items if str(item).strip()]


def parse_review(text: str) -> dict[str, Any]:
    """Parse {"passed": true, "feedback": "..."} from a model response."""
    payload = json.loads(text)
    return {
        "passed": bool(payload.get("passed")),
        "feedback": str(payload.get("feedback", "")).strip(),
    }


class ChecklistAgent(AgentBase):
    """A custom teaching agent loop.

    This loop is program-driven:
    1. create checklist
    2. execute each item
    3. review each result
    4. retry once when needed
    5. summarize all results
    """

    def _create_checklist(self, user_task: str) -> list[str]:
        """TODO 1: ask the model to create checklist items and parse them."""
        raise NotImplementedError("TODO 1: implement checklist creation")

    def _format_previous_results(self, results: list[StepResult]) -> str:
        """TODO 2: format previous step results for the next step prompt."""
        raise NotImplementedError("TODO 2: implement previous result formatting")

    def _execute_item(
        self,
        user_task: str,
        item: str,
        previous_results: list[StepResult],
        *,
        feedback: Optional[str] = None,
    ) -> str:
        """TODO 3: execute one checklist item.

        Suggested structure:
        - create a prompt that includes the original task, current item,
          previous results, and optional feedback
        - create a MinimalAgent as a step executor
        - pass the same llm and tool registry to the executor
        - return executor.run(step_prompt)
        """
        raise NotImplementedError("TODO 3: implement checklist item execution")

    def _review_item(self, item: str, result: str) -> dict[str, Any]:
        """TODO 4: ask the model to review one step result and parse the JSON."""
        raise NotImplementedError("TODO 4: implement step review")

    def _summarize(self, user_task: str, results: list[StepResult]) -> str:
        """TODO 5: ask the model to summarize all step results."""
        raise NotImplementedError("TODO 5: implement final summarization")

    def run(self, input_text: str, **kwargs: Any) -> str:
        """TODO 6: complete the custom agent loop.

        Required behavior:
        - create checklist
        - execute each checklist item
        - review the result
        - if review failed, retry the item once with review feedback
        - save each StepResult
        - summarize all results
        - save the user turn with _save_turn(...)
        - return the final answer
        """
        raise NotImplementedError("TODO 6: implement ChecklistAgent loop")


def build_demo_llm() -> HelloAgentsLLM:
    """Build a deterministic backend for the homework.

    The scripted responses are ordered to match the intended ChecklistAgent loop.
    """
    return HelloAgentsLLM(
        backend=ScriptedLLMBackend(
            [
                {
                    "content": json.dumps(
                        {
                            "items": [
                                "Read the lesson note",
                                "Extract the core ideas",
                                "Write two review cards",
                            ]
                        }
                    )
                },
                {
                    "content": "I will read the lesson note first.",
                    "tool_calls": [
                        {
                            "id": "read-note-1",
                            "name": "read_markdown",
                            "arguments": {"path": str(NOTE_PATH)},
                        }
                    ],
                },
                {
                    "content": (
                        "The lesson note says an Agent organizes an LLM, context, "
                        "tools, and a control loop. It also distinguishes Tool and Skill."
                    )
                },
                {
                    "content": json.dumps(
                        {"passed": True, "feedback": "The lesson note was read."}
                    )
                },
                {
                    "content": "Core ideas: Agent controls the loop; Tool executes actions."
                },
                {
                    "content": json.dumps(
                        {
                            "passed": False,
                            "feedback": "The answer missed Skill and retry/stop decisions.",
                        }
                    )
                },
                {
                    "content": (
                        "Core ideas: Agent organizes LLM, context, tools, and a control loop; "
                        "Tool executes concrete actions; Skill provides reusable task methods; "
                        "agent loops decide context, observations, retry, stop, and summary."
                    )
                },
                {
                    "content": json.dumps(
                        {
                            "passed": True,
                            "feedback": "The revised result covers all core ideas.",
                        }
                    )
                },
                {
                    "content": (
                        "Q: What are the core parts of an Agent?\n"
                        "A: LLM, context, tools, and a control loop.\n\n"
                        "Q: How are Tool and Skill different?\n"
                        "A: Tool executes actions; Skill provides reusable task methods."
                    )
                },
                {
                    "content": json.dumps(
                        {"passed": True, "feedback": "The review cards are clear."}
                    )
                },
                {
                    "content": (
                        "Final answer:\n"
                        "Agent is the controller that organizes the LLM, context, tools, "
                        "and loop decisions. Tool executes concrete actions, while Skill "
                        "provides reusable task methods.\n\n"
                        "Review cards:\n"
                        "Q: What are the core parts of an Agent?\n"
                        "A: LLM, context, tools, and a control loop.\n\n"
                        "Q: How are Tool and Skill different?\n"
                        "A: Tool executes actions; Skill provides reusable task methods."
                    )
                },
            ]
        )
    )


def main() -> None:
    llm = build_demo_llm()
    agent = ChecklistAgent(
        "checklist-homework",
        llm,
        tool_registry=build_tool_registry(),
    )

    task = (
        "Read the lesson note, extract the key ideas, and write two review cards. "
        f"The note path is {NOTE_PATH}."
    )
    print(agent.run(task))


if __name__ == "__main__":
    main()
