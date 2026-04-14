from __future__ import annotations

from .loader import SkillLoader


class SkillResolver:
    def __init__(self, loader: SkillLoader):
        self.loader = loader

    def render(self, skill_name: str, args: str = "") -> str:
        skill = self.loader.get_skill(skill_name)
        if skill is None:
            raise KeyError(f"Skill not found: {skill_name}")
        return skill.body.replace("$ARGUMENTS", args).strip()
