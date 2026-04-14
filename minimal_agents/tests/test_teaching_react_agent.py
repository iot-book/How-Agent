from minimal_agents import ReActAgent, HelloAgentsLLM, ScriptedLLMBackend, ToolRegistry
from minimal_agents.tools.builtin import CalculatorTool


def test_react_agent_finishes_with_builtin_finish():
    backend = ScriptedLLMBackend([
        {
            "content": "thinking",
            "tool_calls": [
                {"id": "t1", "name": "Thought", "arguments": {"reasoning": "Need calculate"}},
                {"id": "t2", "name": "calculator", "arguments": {"expression": "10/2"}},
            ],
        },
        {
            "content": "done",
            "tool_calls": [
                {"id": "t3", "name": "Finish", "arguments": {"answer": "The answer is 5."}},
            ],
        },
    ])

    llm = HelloAgentsLLM(backend=backend)
    registry = ToolRegistry()
    registry.register_tool(CalculatorTool())

    agent = ReActAgent("react", llm, tool_registry=registry)
    output = agent.run("compute 10/2")

    assert output == "The answer is 5."
