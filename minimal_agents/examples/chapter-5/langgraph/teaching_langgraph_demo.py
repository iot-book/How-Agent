"""Teaching demo: use LangGraph to organize a small agent-like workflow.

This demo intentionally does not depend on an online LLM.
It focuses on three ideas:
1. state carries shared data
2. nodes update state
3. edges decide how the workflow moves forward
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


SAMPLE_NOTE_PATH = Path(__file__).resolve().parent / "sample_student_task.md"


class GraphState(TypedDict, total=False):
    task: str
    note_path: str
    route: str
    note_content: str
    summary: str
    final_answer: str


def read_markdown(path: str) -> dict[str, str]:
    """Read a UTF-8 Markdown file from disk."""
    markdown_path = Path(path)
    if not markdown_path.exists():
        return {"path": path, "error": "file not found"}
    content = markdown_path.read_text(encoding="utf-8")
    return {"path": path, "content": content}


def build_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register_function(read_markdown, "Read UTF-8 content from a Markdown file.")
    return registry


REGISTRY = build_tool_registry()


def decide_route(state: GraphState) -> dict[str, str]:
    task = state.get("task", "").lower()
    if "read" in task or "summary" in task or "summarize" in task:
        return {"route": "read_note"}
    return {"route": "direct_answer"}


def route_from_state(state: GraphState) -> str:
    return state.get("route", "direct_answer")


def read_note(state: GraphState) -> dict[str, str]:
    response = REGISTRY.execute_tool("read_markdown", {"path": state["note_path"]})
    content = response.data.get("content", "")
    if not content:
        return {"note_content": "No note content was loaded."}
    return {"note_content": content}


def summarize_note(state: GraphState) -> dict[str, str]:
    content = state.get("note_content", "")
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    headings = [line.lstrip("# ").strip() for line in lines if line.startswith("#")]
    bullets = [line.lstrip("- ").strip() for line in lines if line.startswith("-")]
    summary_lines = [
        "Summary from LangGraph workflow:",
        f"- headings: {', '.join(headings[:3]) or 'none'}",
        f"- key points: {'; '.join(bullets[:4]) or 'none'}",
    ]
    return {"summary": "\n".join(summary_lines)}


def answer_without_note(state: GraphState) -> dict[str, str]:
    return {
        "final_answer": (
            "This task does not require reading a Markdown file, "
            "so the workflow returned a direct answer."
        )
    }


def finalize_with_summary(state: GraphState) -> dict[str, str]:
    return {
        "final_answer": (
            f"Task: {state.get('task', '')}\n"
            f"Note path: {state.get('note_path', '')}\n"
            f"{state.get('summary', '')}"
        )
    }


def build_app():
    graph = StateGraph(GraphState)
    graph.add_node("decide_route", decide_route)
    graph.add_node("read_note", read_note)
    graph.add_node("summarize_note", summarize_note)
    graph.add_node("answer_without_note", answer_without_note)
    graph.add_node("finalize_with_summary", finalize_with_summary)

    graph.add_edge(START, "decide_route")
    graph.add_conditional_edges(
        "decide_route",
        route_from_state,
        {
            "read_note": "read_note",
            "direct_answer": "answer_without_note",
        },
    )
    graph.add_edge("read_note", "summarize_note")
    graph.add_edge("summarize_note", "finalize_with_summary")
    graph.add_edge("answer_without_note", END)
    graph.add_edge("finalize_with_summary", END)
    return graph.compile()


def main() -> None:
    app = build_app()
    result = app.invoke(
        {
            "task": "Read the markdown note and summarize the core ideas.",
            "note_path": str(SAMPLE_NOTE_PATH),
        }
    )
    print(result["final_answer"])


if __name__ == "__main__":
    main()
