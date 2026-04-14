from minimal_agents import MinimalAgent, HelloAgentsLLM, ScriptedLLMBackend, ToolRegistry
from minimal_agents.tools.builtin import CalculatorTool


def test_minimal_agent_direct_answer():
    llm = HelloAgentsLLM(backend=ScriptedLLMBackend([
        {"content": "direct answer"}
    ]))
    agent = MinimalAgent("mini", llm)

    output = agent.run("say something")
    assert output == "direct answer"


def test_minimal_agent_tool_loop():
    backend = ScriptedLLMBackend([
        {
            "content": "I'll calculate",
            "tool_calls": [
                {"id": "c1", "name": "calculator", "arguments": {"expression": "2+3"}}
            ],
        },
        {"content": "The result is 5."},
    ])
    llm = HelloAgentsLLM(backend=backend)
    registry = ToolRegistry()
    registry.register_tool(CalculatorTool())

    agent = MinimalAgent("mini", llm, tool_registry=registry)
    output = agent.run("what is 2+3")

    assert "5" in output
