from pathlib import Path

from minimal_agents.skills import SkillLoader, SkillResolver


def test_skill_loader_and_resolver(tmp_path: Path):
    skill_dir = tmp_path / "skills" / "summarize"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: summarize
description: Summarize long content
---
Use concise bullets.
Input:
$ARGUMENTS
""",
        encoding="utf-8",
    )

    loader = SkillLoader(tmp_path / "skills")
    assert loader.list_skills() == ["summarize"]
    assert "Summarize long content" in loader.get_descriptions()

    skill = loader.get_skill("summarize")
    assert skill is not None
    assert "Use concise bullets." in skill.body

    resolver = SkillResolver(loader)
    rendered = resolver.render("summarize", "A very long paragraph")
    assert "A very long paragraph" in rendered


def test_loader_reload(tmp_path: Path):
    root = tmp_path / "skills"
    first = root / "a"
    first.mkdir(parents=True)
    (first / "SKILL.md").write_text("---\nname: a\n---\nA", encoding="utf-8")

    loader = SkillLoader(root)
    assert loader.list_skills() == ["a"]

    second = root / "b"
    second.mkdir(parents=True)
    (second / "SKILL.md").write_text("---\nname: b\n---\nB", encoding="utf-8")

    loader.reload()
    assert loader.list_skills() == ["a", "b"]
