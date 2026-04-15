"""Fill-in-the-blank exercise for the LangGraph section.

Goal:
1. define a small shared state
2. route a task through conditional edges
3. call a minimal_agents tool inside a graph node
4. summarize Markdown content
5. compile a runnable StateGraph
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


def bootstrap() -> None:
    project_root = Path(__file__).resolve().parents[3]
    src_path = project_root / "src"
    src_str = str(src_path)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


bootstrap()

from minimal_agents import ToolRegistry


NOTE_PATH = Path(__file__).resolve().parent / "sample_student_handbook.md"


class HomeworkState(TypedDict, total=False):
    task: str
    note_path: str
    route: str
    note_content: str
    summary: str
    final_answer: str


def read_markdown(path: str) -> dict[str, str]:
    """Read a UTF-8 Markdown file."""
    markdown_path = Path(path)
    if not markdown_path.exists():
        return {"path": path, "error": "file not found"}
    return {"path": path, "content": markdown_path.read_text(encoding="utf-8")}


def build_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register_function(read_markdown, "Read UTF-8 content from a Markdown file.")
    return registry


REGISTRY = build_tool_registry()


def decide_route(state: HomeworkState) -> dict[str, str]:
    """TODO 1: inspect the task and return {"route": "..."}.

    Suggested behavior:
    - if the task asks to read/summarize the note, return {"route": "read_note"}
    - otherwise return {"route": "direct_answer"}
    """
    raise NotImplementedError("TODO 1: implement route decision")


def route_from_state(state: HomeworkState) -> str:
    """TODO 2: return the route name stored in state.

    The return value will be used by add_conditional_edges(...).
    """
    raise NotImplementedError("TODO 2: implement route lookup")


def read_note(state: HomeworkState) -> dict[str, str]:
    """TODO 3: execute the registered tool and write note_content into state."""
    raise NotImplementedError("TODO 3: implement tool execution in a graph node")


def summarize_note(state: HomeworkState) -> dict[str, str]:
    """TODO 4: summarize headings and bullet points from the Markdown note.

    Suggested structure:
    - split content into lines
    - collect headings starting with '#'
    - collect bullet points starting with '-'
    - return {"summary": "..."}
    """
    raise NotImplementedError("TODO 4: implement markdown summarization")


def answer_without_note(state: HomeworkState) -> dict[str, str]:
    return {
        "final_answer": "The task does not require reading a note, so the graph returned directly."
    }


def finalize_with_summary(state: HomeworkState) -> dict[str, str]:
    return {
        "final_answer": (
            f"Task: {state.get('task', '')}\n"
            f"Summary:\n{state.get('summary', '')}"
        )
    }


def build_app():
    """TODO 5: create the graph, add nodes, add edges, and compile it.

    Expected flow:
    START -> decide_route
    decide_route -> read_note OR answer_without_note
    read_note -> summarize_note -> finalize_with_summary -> END
    answer_without_note -> END
    """
    raise NotImplementedError("TODO 5: implement StateGraph construction")


def main() -> None:
    app = build_app()
    result = app.invoke(
        {
            "task": "Read the markdown note and summarize the core ideas.",
            "note_path": str(NOTE_PATH),
        }
    )
    print(result["final_answer"])


if __name__ == "__main__":
    main()
