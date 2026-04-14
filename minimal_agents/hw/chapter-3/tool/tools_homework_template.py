"""Fill-in-the-blank exercise for the Tools chapter.

Goal:
1. implement a tool that reads a Markdown file
2. register the tool
3. update the scripted tool call
4. complete the final answer
"""

from pathlib import Path
import sys


def bootstrap() -> None:
    project_root = Path(__file__).resolve().parents[3]
    src_path = project_root / "src"
    src_str = str(src_path)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


bootstrap()

from minimal_agents import HelloAgentsLLM, MinimalAgent, ScriptedLLMBackend, ToolRegistry

HOMEWORK_MD_PATH = Path(__file__).resolve().parent / "sample_note.md"


def read_markdown(path: str) -> dict:
    """TODO: read a Markdown file and return structured content.

    Suggested return shape:
    {
        "path": path,
        "content": "...",
    }

    If the file does not exist, you can return:
    {
        "path": path,
        "error": "file not found",
    }
    """

    raise NotImplementedError("TODO: implement read_markdown")


def main() -> None:
    registry = ToolRegistry()

    # TODO: register read_markdown as a tool.
    # Example:
    # registry.register_function(
    #     read_markdown,
    #     "Read UTF-8 content from a Markdown file.",
    # )

    llm = HelloAgentsLLM(
        backend=ScriptedLLMBackend(
            [
                {
                    "content": "我先读取 Markdown 文件。",
                    "tool_calls": [
                        {
                            "id": "tool-1",
                            # TODO: fill in the tool name.
                            "name": "TODO_TOOL_NAME",
                            # TODO: pass the file path.
                            "arguments": {"path": "TODO_MD_PATH"},
                        }
                    ],
                },
                {
                    # TODO: update the final answer based on the file content.
                    "content": "TODO_FINAL_ANSWER",
                },
            ]
        )
    )

    agent = MinimalAgent("tools-homework", llm, tool_registry=registry)

    # TODO: update the task so it matches the file-reading scenario.
    print(agent.run("TODO_USER_TASK"))


if __name__ == "__main__":
    main()
