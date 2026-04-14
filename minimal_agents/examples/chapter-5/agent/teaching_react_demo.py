"""Teaching demo: ReActAgent with Thought/Finish."""

from _bootstrap import bootstrap

bootstrap()

from minimal_agents import ReActAgent, HelloAgentsLLM, ScriptedLLMBackend, ToolRegistry
from minimal_agents.tools.builtin import CalculatorTool


def main() -> None:
    backend = ScriptedLLMBackend([
        {
            "content": "reasoning",
            "tool_calls": [
                {"id": "1", "name": "Thought", "arguments": {"reasoning": "Need calculator"}},
                {"id": "2", "name": "calculator", "arguments": {"expression": "6*7"}},
            ],
        },
        {
            "content": "finish",
            "tool_calls": [
                {"id": "3", "name": "Finish", "arguments": {"answer": "42"}},
            ],
        },
    ])
    llm = HelloAgentsLLM(backend=backend)
    registry = ToolRegistry()
    registry.register_tool(CalculatorTool())

    agent = ReActAgent("react-demo", llm, tool_registry=registry)
    print(agent.run("what is 6*7"))


if __name__ == "__main__":
    main()
