"""Fill-in-the-blank exercise for the Gateway chapter.

Goal:
1. read WebSocket-like frames from different channels
2. normalize them into a unified request format
3. route them through a simple gateway
4. forward the request to MinimalAgent
5. wrap the agent result into a unified response
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
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

HOMEWORK_MD_PATH = Path(__file__).resolve().parent / "gateway_homework_note.md"


def read_markdown_overview(path: str) -> dict:
    """A ready-made tool used by this homework."""
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")

    title = "Untitled"
    headings: list[str] = []
    bullet_count = 0

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
        elif stripped.startswith("## "):
            headings.append(stripped[3:].strip())
        elif stripped.startswith("- "):
            bullet_count += 1

    return {
        "text": f"Read markdown file: {file_path.name}",
        "path": file_path.name,
        "title": title,
        "headings": headings,
        "bullet_count": bullet_count,
    }


@dataclass(slots=True)
class GatewayRequest:
    channel: str
    user_id: str
    session_id: str
    message: str


@dataclass(slots=True)
class GatewayResponse:
    channel: str
    session_id: str
    agent_name: str
    reply: str


class SimpleGateway:
    """TODO: complete a minimal gateway."""

    def __init__(self) -> None:
        # TODO: store route -> agent mapping here.
        self._routes = {}

    def register_agent(self, route: str, agent: MinimalAgent) -> None:
        # TODO: save the agent into self._routes.
        raise NotImplementedError("TODO: implement register_agent")

    def normalize_frame(self, frame: dict) -> GatewayRequest:
        """TODO: convert a WebSocket-like frame into GatewayRequest.

        The incoming frame uses this shape:
        {
            "type": "message",
            "channel": "...",
            "user_id": "...",
            "session_id": "...",
            "text": "..."
        }
        """

        # TODO:
        # 1. read channel / user_id / session_id / text from the frame
        # 2. build and return GatewayRequest(...)
        raise NotImplementedError("TODO: implement normalize_frame")

    def dispatch_frame(self, route: str, frame: dict) -> GatewayResponse:
        """TODO: route one incoming frame through the gateway."""

        # Suggested steps:
        # 1. call normalize_frame(frame)
        # 2. fetch the target agent from self._routes
        # 3. optionally wrap the original message with channel/session metadata
        # 4. call agent.run(...)
        # 5. return GatewayResponse(...)
        raise NotImplementedError("TODO: implement dispatch_frame")


def build_demo_agent(sample_path: Path) -> MinimalAgent:
    """This part is already completed so the homework stays focused on Gateway."""
    registry = ToolRegistry()
    registry.register_function(
        read_markdown_overview,
        "Read a Markdown file and return its title, headings, and bullet count.",
    )

    def first_turn(messages, tools):
        return {
            "content": "I will inspect the markdown note before answering.",
            "tool_calls": [
                {
                    "id": "gw-tool-1",
                    "name": "read_markdown_overview",
                    "arguments": {"path": str(sample_path)},
                }
            ],
        }

    def second_turn(messages, tools):
        tool_payload = {}
        for message in messages:
            if message.get("role") == "tool" and message.get("name") == "read_markdown_overview":
                tool_payload = json.loads(message["content"])

        data = tool_payload.get("data", {})
        title = data.get("title", "Unknown title")
        headings = " / ".join(data.get("headings", [])) or "No section headings"
        bullet_count = data.get("bullet_count", 0)

        return {
            "content": (
                f"标题：《{title}》；"
                f"小节：{headings}；"
                f"列表项数量：{bullet_count}。"
            )
        }

    llm = HelloAgentsLLM(
        backend=ScriptedLLMBackend([first_turn, second_turn, first_turn, second_turn, first_turn, second_turn])
    )
    return MinimalAgent("gateway-homework-agent", llm, tool_registry=registry)


def main() -> None:
    gateway = SimpleGateway()

    # TODO: register the demo agent under a route name such as "study-assistant".
    # Example:
    # gateway.register_agent("study-assistant", build_demo_agent(HOMEWORK_MD_PATH))

    incoming_frames = [
        {
            "type": "message",
            "channel": "web",
            "user_id": "student-web-001",
            "session_id": "session-web-001",
            "text": "请读取这份 Markdown，并介绍它的结构。",
        },
        {
            "type": "message",
            "channel": "feishu",
            "user_id": "student-feishu-002",
            "session_id": "session-feishu-002",
            "text": "同样读取这份 Markdown，并概括主要内容。",
        },
        {
            "type": "message",
            "channel": "cli",
            "user_id": "student-cli-003",
            "session_id": "session-cli-003",
            "text": "请基于这份 Markdown 给出一句简短总结。",
        },
    ]

    for frame in incoming_frames:
        # TODO: replace the route name and make dispatch_frame(...) work.
        response = gateway.dispatch_frame("TODO_ROUTE_NAME", frame)
        print(json.dumps(asdict(response), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
