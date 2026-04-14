"""Teaching demo: a minimal gateway in front of MinimalAgent."""

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
from teaching_gateway_tools import read_markdown_overview


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
    """Normalize external requests and route them to the correct agent."""

    def __init__(self) -> None:
        self._routes: dict[str, MinimalAgent] = {}

    def register_agent(self, route: str, agent: MinimalAgent) -> None:
        self._routes[route] = agent

    def dispatch(self, route: str, request: GatewayRequest) -> GatewayResponse:
        agent = self._routes[route]
        normalized_prompt = self._normalize_request(request)
        reply = agent.run(normalized_prompt)
        return GatewayResponse(
            channel=request.channel,
            session_id=request.session_id,
            agent_name=route,
            reply=reply,
        )

    def _normalize_request(self, request: GatewayRequest) -> str:
        return (
            f"[channel={request.channel}] "
            f"[user={request.user_id}] "
            f"[session={request.session_id}] "
            f"{request.message}"
        )


def build_demo_agent(sample_path: Path) -> MinimalAgent:
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
        latest_user_message = ""

        for message in messages:
            if message.get("role") == "user":
                latest_user_message = message.get("content", "")
            if message.get("role") == "tool" and message.get("name") == "read_markdown_overview":
                tool_payload = json.loads(message["content"])

        data = tool_payload.get("data", {})
        title = data.get("title", "Unknown title")
        headings = " / ".join(data.get("headings", [])) or "No section headings"
        bullet_count = data.get("bullet_count", 0)

        return {
            "content": (
                f"已通过 Gateway 将请求转发给 MinimalAgent。"
                f"这份 Markdown 的标题是《{title}》，"
                f"主要小节包括：{headings}，"
                f"其中共有 {bullet_count} 个列表项。"
                f"原始接入请求为：{latest_user_message}"
            )
        }

    llm = HelloAgentsLLM(backend=ScriptedLLMBackend([first_turn, second_turn, first_turn, second_turn]))
    return MinimalAgent("gateway-demo-agent", llm, tool_registry=registry)


def main() -> None:
    sample_path = Path(__file__).with_name("gateway_sample_note.md")
    gateway = SimpleGateway()
    gateway.register_agent("study-assistant", build_demo_agent(sample_path))

    requests = [
        GatewayRequest(
            channel="web",
            user_id="student-web-001",
            session_id="session-web-001",
            message="请读取这份 Markdown，并用教学语言介绍它的结构。",
        ),
        GatewayRequest(
            channel="feishu",
            user_id="student-feishu-007",
            session_id="session-feishu-007",
            message="同样的问题，请继续根据同一份 Markdown 给出说明。",
        ),
    ]

    for request in requests:
        response = gateway.dispatch("study-assistant", request)
        print(json.dumps(asdict(response), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
