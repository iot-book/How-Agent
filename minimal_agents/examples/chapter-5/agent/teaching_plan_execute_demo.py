"""Teaching demo: PlanAndExecuteAgent."""

from _bootstrap import bootstrap

bootstrap()

from minimal_agents import PlanAndExecuteAgent, HelloAgentsLLM, ScriptedLLMBackend, ToolRegistry


def main() -> None:
    llm = HelloAgentsLLM(backend=ScriptedLLMBackend([
        {"content": '{"steps": ["Collect facts", "Summarize"]}'},
        {"content": "Facts collected."},
        {"content": "Draft summary."},
        {"content": "Final answer from plan-and-execute."},
    ]))
    agent = PlanAndExecuteAgent("pae-demo", llm, tool_registry=ToolRegistry())
    print(agent.run("summarize this project"))


if __name__ == "__main__":
    main()
