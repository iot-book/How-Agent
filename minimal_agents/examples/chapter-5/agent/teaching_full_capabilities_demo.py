"""Teaching demo: one task using skill + local tool + MCP tool."""

from __future__ import annotations

import json
from pathlib import Path

from _bootstrap import bootstrap

bootstrap()

from minimal_agents import HelloAgentsLLM, MinimalAgent, ScriptedLLMBackend, ToolRegistry
from minimal_agents.mcp import InMemoryMCPClient, register_mcp_tools
from minimal_agents.skills import SkillLoader, SkillResolver


def extract_focus(topic: str) -> dict:
    """Extract the focus term from a beginner study-card request."""
    cleaned = topic.replace("请给", "").replace("做一张入门学习卡片", "").strip("：: ，,。.")
    return {"text": f"focus term: {cleaned}", "focus": cleaned}


def build_demo_agent() -> tuple[MinimalAgent, ScriptedLLMBackend]:
    skills_root = Path(__file__).resolve().parent / "skills_demo"
    resolver = SkillResolver(SkillLoader(skills_root))

    registry = ToolRegistry()
    registry.register_function(extract_focus)

    client = InMemoryMCPClient()
    client.register_tool(
        "lookup_fact",
        "Look up one concise teaching fact for a topic",
        lambda topic: {
            "text": f"fact: {topic} lets plants convert light into stored chemical energy and release oxygen.",
            "topic": topic,
            "fact": "植物把光能转成储存起来的化学能，并释放氧气。",
        },
        parameters={
            "type": "object",
            "properties": {"topic": {"type": "string", "description": "topic name"}},
            "required": ["topic"],
        },
    )
    register_mcp_tools(client, registry)

    def first_turn(messages, tools):
        assert tools is not None
        tool_names = {tool["function"]["name"] for tool in tools}
        assert tool_names == {"extract_focus", "mcp_lookup_fact"}
        assert "标题：..." in messages[0]["content"]
        assert "标题和内容各一行" in messages[0]["content"]
        return {
            "content": "I need the core topic and one factual teaching note.",
            "tool_calls": [
                {"id": "tool-1", "name": "extract_focus", "arguments": {"topic": messages[-1]["content"]}},
                {"id": "tool-2", "name": "mcp_lookup_fact", "arguments": {"topic": "光合作用"}},
            ],
        }

    def second_turn(messages, tools):
        tool_payloads = {
            message["name"]: json.loads(message["content"])
            for message in messages
            if message["role"] == "tool"
        }
        focus = tool_payloads["extract_focus"]["data"]["focus"]
        fact = tool_payloads["mcp_lookup_fact"]["data"]["fact"]
        return {
            "content": f"标题：{focus}\n内容：{fact}",
        }

    backend = ScriptedLLMBackend([first_turn, second_turn])
    agent = MinimalAgent(
        "full-capabilities-demo",
        HelloAgentsLLM(backend=backend),
        tool_registry=registry,
        skill_resolver=resolver,
    )
    return agent, backend


def run_demo() -> str:
    agent, _ = build_demo_agent()
    return agent.run(
        "请给光合作用做一张入门学习卡片",
        skill="study_card",
        skill_args="标题和内容各一行，每行尽量短。",
    )


def main() -> None:
    agent, _ = build_demo_agent()
    print("skills:", ["study_card"])
    print("tools:", agent.tool_registry.list_tools())
    print(
        agent.run(
            "请给光合作用做一张入门学习卡片",
            skill="study_card",
            skill_args="标题和内容各一行，每行尽量短。",
        )
    )


if __name__ == "__main__":
    main()
