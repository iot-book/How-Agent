"""Teaching demo: MinimalAgent with a deterministic backend."""

from _bootstrap import bootstrap

bootstrap()

from minimal_agents import MinimalAgent, HelloAgentsLLM, ScriptedLLMBackend


def main() -> None:
    llm = HelloAgentsLLM(backend=ScriptedLLMBackend([
        {"content": "Hello from MinimalAgent (teaching demo)."}
    ]))
    agent = MinimalAgent("minimal-demo", llm)
    print(agent.run("say hello"))


if __name__ == "__main__":
    main()
