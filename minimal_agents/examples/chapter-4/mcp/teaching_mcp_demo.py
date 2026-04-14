"""Teaching demo: connect MinimalAgent to a local stdio MCP server."""

import json
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
from minimal_agents.mcp import StdioMCPClient, register_mcp_tools


def extract_string_list(value):
    """Find the first list[str] inside a nested MCP payload."""

    if isinstance(value, list):
        if all(isinstance(item, str) for item in value):
            return value
        for item in value:
            result = extract_string_list(item)
            if result:
                return result
        return None

    if isinstance(value, dict):
        for item in value.values():
            result = extract_string_list(item)
            if result:
                return result
        return None

    return None


def main() -> None:
    examples_dir = Path(__file__).resolve().parent
    client = StdioMCPClient(
        command=sys.executable,
        args=["teaching_stdio_weather_server.py"],
        cwd=examples_dir,
    )

    registry = ToolRegistry()
    register_mcp_tools(client, registry)

    def first_turn(messages, tools):
        return {
            "content": "我先查询支持的城市，再查询上海天气。",
            "tool_calls": [
                {"id": "m1", "name": "mcp_list_supported_cities", "arguments": {}},
                {"id": "m2", "name": "mcp_get_weather", "arguments": {"city": "Shanghai"}},
            ],
        }

    def second_turn(messages, tools):
        tool_payloads = {}
        for message in messages:
            if message.get("role") != "tool":
                continue
            content = message.get("content", "")
            try:
                tool_payloads[message["name"]] = json.loads(content)
            except json.JSONDecodeError:
                tool_payloads[message["name"]] = {"text": content, "data": {}}

        supported = tool_payloads.get("mcp_list_supported_cities", {})
        weather = tool_payloads.get("mcp_get_weather", {})

        supported_data = supported.get("data", {})
        cities = extract_string_list(supported_data)
        if cities is None:
            raw_text = supported.get("text", "").strip()
            if raw_text.startswith("[") and raw_text.endswith("]"):
                try:
                    parsed = json.loads(raw_text.replace("'", "\""))
                    cities = extract_string_list(parsed)
                except json.JSONDecodeError:
                    cities = None
        if not isinstance(cities, list):
            cities = []

        weather_text = weather.get("text", "未获取到天气结果")
        city_list = "、".join(cities) if cities else "未知"

        return {
            "content": (
                f"已通过 MCP Server 查询到支持的城市有：{city_list}。"
                f"其中上海天气为：{weather_text}。"
            )
        }

    llm = HelloAgentsLLM(
        backend=ScriptedLLMBackend(
            [first_turn, second_turn]
        )
    )

    agent = MinimalAgent("mcp-demo", llm, tool_registry=registry)
    print(agent.run("查询上海天气"))


if __name__ == "__main__":
    main()
