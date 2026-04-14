"""Teaching demo: skill-guided Markdown reading with a real file-read step."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


def bootstrap() -> None:
    project_root = Path(__file__).resolve().parents[3]
    src_path = project_root / "src"
    src_str = str(src_path)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


bootstrap()

from minimal_agents import HelloAgentsLLM, MinimalAgent, ScriptedLLMBackend, ToolRegistry
from minimal_agents.skills import SkillLoader, SkillResolver

SKILLS_ROOT = Path(__file__).resolve().parent / "skills_demo"
SOURCE_PATH = SKILLS_ROOT / "markdown_reader" / "sample_source.md"


def choose_skill(user_task: str) -> tuple[str | None, str]:
    """Tiny rule-based router used to explain auto-selection."""

    lowered = user_task.lower()
    if any(
        keyword in lowered
        for keyword in ["markdown", "read", "reader", "summary", "summarize", "note"]
    ):
        return (
            "markdown_reader",
            "Read the source Markdown file first, then explain it for beginner readers.",
        )
    return None, ""


def build_skill_args(skill_name: str, source_path: Path) -> str:
    """Run an attached helper script inside the skill directory."""

    script_path = SKILLS_ROOT / skill_name / "scripts" / "read_markdown_source.py"
    completed = subprocess.run(
        [sys.executable, str(script_path), str(source_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def read_markdown_file(path: str) -> dict:
    """Read UTF-8 content from a Markdown file."""

    file_path = Path(path)
    if not file_path.exists():
        return {"path": str(file_path), "error": "file not found"}
    return {
        "path": str(file_path),
        "content": file_path.read_text(encoding="utf-8"),
    }


def build_demo_agent() -> MinimalAgent:
    resolver = SkillResolver(SkillLoader(SKILLS_ROOT))

    registry = ToolRegistry()
    registry.register_function(
        read_markdown_file,
        "Read UTF-8 content from a Markdown file.",
    )

    def first_turn(messages, tools):
        system_prompt = messages[0]["content"]
        if "Markdown Reader Skill" not in system_prompt:
            return {"content": "This run did not inject the markdown_reader skill."}

        return {
            "content": "I should read the Markdown source file before summarizing it.",
            "tool_calls": [
                {
                    "id": "tool-1",
                    "name": "read_markdown_file",
                    "arguments": {"path": str(SOURCE_PATH)},
                }
            ],
        }

    def second_turn(messages, tools):
        tool_payload = {}
        for message in messages:
            if message.get("role") != "tool":
                continue
            if message.get("name") != "read_markdown_file":
                continue
            tool_payload = json.loads(message["content"])
            break

        source_data = tool_payload.get("data", {})
        content = source_data.get("content", "")
        if not content:
            return {"content": "未能读取到 Markdown 文件内容。"}

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        title = next((line.lstrip("# ").strip() for line in lines if line.startswith("# ")), "Untitled")
        sections = [line.lstrip("# ").strip() for line in lines if line.startswith("## ")]

        bullets = []
        for line in lines:
            if line.startswith("- "):
                bullets.append(line[2:].strip())

        section_text = "、".join(sections[:3]) if sections else "无"
        bullet_text = "；".join(bullets[:3]) if bullets else "无"

        return {
            "content": (
                f"# {title} 阅读说明\n\n"
                f"## 核心结构\n"
                f"这份 Markdown 主要包括：{section_text}。\n\n"
                f"## 关键信息\n"
                f"{bullet_text if bullet_text != '无' else '文档重点主要通过段落说明给出。'}"
            )
        }

    llm = HelloAgentsLLM(
        backend=ScriptedLLMBackend([first_turn, second_turn, first_turn, second_turn])
    )

    # If you want to use a real online model, replace the llm above
    # with the block below and fill in your actual parameters.
    #
    # llm = HelloAgentsLLM(
    #     model="YOUR_MODEL_NAME",cd 
    #     api_key="YOUR_API_KEY",
    #     base_url="YOUR_BASE_URL",
    # )


    return MinimalAgent(
        "skills-demo",
        llm,
        tool_registry=registry,
        skill_resolver=resolver,
    )


def run_auto_skill_demo(agent: MinimalAgent, user_task: str) -> None:
    print("=== Auto skill routing ===")
    skill_name, skill_args = choose_skill(user_task)

    if skill_name is None:
        print(agent.run(user_task))
        return

    rendered_args = build_skill_args(skill_name, SOURCE_PATH)

    print(
        agent.run(
            user_task,
            skill=skill_name,
            skill_args=f"{skill_args}\n\n{rendered_args}",
        )
    )


def run_manual_override_demo(agent: MinimalAgent) -> None:
    print("\n=== Manual override for testing ===")
    user_task = "Read the Markdown source and explain its main points."
    rendered_args = build_skill_args("markdown_reader", SOURCE_PATH)
    print(
        agent.run(
            user_task,
            skill="markdown_reader",
            skill_args=(
                "Read the source Markdown file first, then explain the structure and key points.\n\n"
                f"{rendered_args}"
            ),
        )
    )


def main() -> None:
    agent = build_demo_agent()
    run_auto_skill_demo(agent, "Read this Markdown note and summarize the key points.")
    run_manual_override_demo(agent)


if __name__ == "__main__":
    main()
