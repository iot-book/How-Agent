"""Teaching demo: prompt wiring inside MinimalAgent."""

from pathlib import Path
import sys


def bootstrap() -> None:
    project_root = Path(__file__).resolve().parents[3]
    src_path = project_root / "src"
    src_str = str(src_path)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


bootstrap()

from minimal_agents import HelloAgentsLLM, MinimalAgent, ScriptedLLMBackend


def main() -> None:
    backend = ScriptedLLMBackend(
        [
            {
                "content": "结论：Tool 是模型可以调用的外部能力接口。",
            }
        ]
    )
    llm = HelloAgentsLLM(backend=backend)
    agent = MinimalAgent(
        "prompt-demo",
        llm,
        system_prompt=(
            "你是一名智能体课程助教。回答时先给结论，再补充一条简短说明。"
        ),
    )

    result = agent.run("什么是 Tool？")
    print(result)
    print("\n--- injected system prompt ---")
    print(backend.calls[0]["messages"][0]["content"])


if __name__ == "__main__":
    main()
