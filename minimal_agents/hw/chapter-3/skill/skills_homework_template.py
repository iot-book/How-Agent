"""Fill-in-the-blank exercise for the Skills chapter.

Goal:
1. complete a skill file
2. load the skill with SkillLoader and SkillResolver
3. choose the skill for a matching task
4. run the agent with the selected skill
"""

from pathlib import Path
import sys


def bootstrap() -> None:
    # The homework lives under minimal_agents/hw/..., so we first
    # add minimal_agents/src into sys.path to import the framework code.
    project_root = Path(__file__).resolve().parents[3]
    src_path = project_root / "src"
    src_str = str(src_path)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


bootstrap()

from minimal_agents import HelloAgentsLLM, MinimalAgent, ScriptedLLMBackend
from minimal_agents.skills import SkillLoader, SkillResolver


def choose_skill(user_task: str) -> tuple[str | None, str]:
    """TODO: select a skill for the current task.

    Suggested idea:
    - if the task is about study notes or study cards, return the skill name
    - otherwise return (None, "")
    """

    # TODO:
    # 1. inspect the user task
    # 2. decide whether this task should use your study_card_writer skill
    # 3. return both the skill name and a short skill argument
    return None, ""


def build_demo_agent() -> MinimalAgent:
    # This directory contains the skill folders. Each skill should live in:
    # skills_demo/<skill_name>/SKILL.md
    skills_root = Path(__file__).resolve().parent / "skills_demo"

    # SkillLoader scans the directory and SkillResolver is passed into the agent,
    # so the agent can fetch the selected skill during execution.
    resolver = SkillResolver(SkillLoader(skills_root))

    # ScriptedLLMBackend keeps the homework deterministic.
    # Students can focus on the skill-loading flow instead of model variance.
    llm = HelloAgentsLLM(
        backend=ScriptedLLMBackend(
            [
                {
                    # TODO:
                    # Replace this with output that matches the workflow you wrote
                    # in study_card_writer/SKILL.md.
                    "content": "TODO: replace this with a response that matches your skill workflow."
                }
            ]
        )
    )

    # Passing skill_resolver into MinimalAgent is the key step that enables
    # skill loading for the current agent.
    return MinimalAgent("skills-homework", llm, skill_resolver=resolver)


def main() -> None:
    agent = build_demo_agent()

    # TODO: write a task that should trigger your study_card_writer skill.
    user_task = "TODO_USER_TASK"

    # The routing step usually happens before agent.run(...).
    # It decides whether we should inject a skill for this task.
    skill_name, skill_args = choose_skill(user_task)

    print(
        agent.run(
            user_task,
            # If choose_skill(...) returns a skill name, the agent will load the
            # corresponding SKILL.md and inject it into the current run.
            skill=skill_name,
            skill_args=skill_args,
        )
    )


if __name__ == "__main__":
    main()
