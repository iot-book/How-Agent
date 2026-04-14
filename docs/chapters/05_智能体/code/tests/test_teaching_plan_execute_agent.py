from minimal_agents import PlanAndExecuteAgent, HelloAgentsLLM, ScriptedLLMBackend, ToolRegistry


def test_plan_execute_agent_runs_plan_and_summary():
    backend = ScriptedLLMBackend([
        {"content": '{"steps": ["Find numbers", "Compute sum"]}'},
        {"content": "Step1 done"},
        {"content": "Step2 done"},
        {"content": "Final: sum is 42"},
    ])

    llm = HelloAgentsLLM(backend=backend)
    agent = PlanAndExecuteAgent("planner", llm, tool_registry=ToolRegistry())

    output = agent.run("calculate final sum")
    assert output == "Final: sum is 42"
