"""Teaching demo: register local tools and use them from MinimalAgent."""

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
from teaching_weather_tool import get_weather


def main() -> None:
    registry = ToolRegistry()
    registry.register_function(
        get_weather,
        "Get weather data for a supported city.",
    )

    def first_turn(messages, tools):
        return {
            "content": "I will call a tool.",
            "tool_calls": [
                {
                    "id": "tool-1",
                    "name": "get_weather",
                    "arguments": {"city": "Shanghai"},
                }
            ],
        }

    def second_turn(messages, tools):
        weather_payload = {}
        for message in messages:
            if message.get("role") != "tool":
                continue
            if message.get("name") != "get_weather":
                continue
            weather_payload = json.loads(message["content"])
            break

        city = weather_payload.get("data", {}).get("city", "未知城市")
        weather = weather_payload.get("data", {}).get("weather", "未知天气")
        temperature = weather_payload.get("data", {}).get("temperature_c", "未知温度")
        return {"content": f"{city}当前{weather}，气温 {temperature}C。"}

    llm = HelloAgentsLLM(
        backend=ScriptedLLMBackend([first_turn, second_turn])
    )

    agent = MinimalAgent("tools-demo", llm, tool_registry=registry)
    print(agent.run("查询背景天气"))


if __name__ == "__main__":
    main()
