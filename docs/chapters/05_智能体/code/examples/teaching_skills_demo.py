"""Teaching demo: skills loading and injection."""

from pathlib import Path

from _bootstrap import bootstrap

bootstrap()

from minimal_agents import MinimalAgent, HelloAgentsLLM, ScriptedLLMBackend
from minimal_agents.skills import SkillLoader, SkillResolver


def main() -> None:
    demo_root = Path(__file__).resolve().parent / "_teaching_demo_skills"
    skill_path = demo_root / "qa"
    skill_path.mkdir(parents=True, exist_ok=True)
    (skill_path / "SKILL.md").write_text(
        """---
name: qa
description: answer concise
---
You should answer in one short paragraph.
Task:
$ARGUMENTS
""",
        encoding="utf-8",
    )

    resolver = SkillResolver(SkillLoader(demo_root))
    llm = HelloAgentsLLM(
        backend=ScriptedLLMBackend([{"content": "Skill was injected and used."}])
    )
    agent = MinimalAgent("skills-demo", llm, skill_resolver=resolver)

    print(
        agent.run(
            "explain agent loop", skill="qa", skill_args="explain in plain language"
        )
    )


if __name__ == "__main__":
    main()
