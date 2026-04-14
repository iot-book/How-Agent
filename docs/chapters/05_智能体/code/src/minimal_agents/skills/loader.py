from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml


@dataclass(slots=True)
class Skill:
    name: str
    description: str
    body: str
    path: Path


class SkillLoader:
    """Load markdown-based skills with optional YAML frontmatter."""

    def __init__(self, skills_dir: Path | str):
        self.skills_dir = Path(skills_dir)
        self._metadata: Dict[str, Dict[str, str]] = {}
        self._cache: Dict[str, Skill] = {}
        self.reload()

    def reload(self) -> None:
        self._metadata.clear()
        self._cache.clear()
        if not self.skills_dir.exists():
            return

        for skill_file in self.skills_dir.glob("*/SKILL.md"):
            raw = skill_file.read_text(encoding="utf-8")
            meta, _ = self._split_frontmatter(raw)
            inferred_name = skill_file.parent.name
            skill_name = str(meta.get("name") or inferred_name)
            self._metadata[skill_name] = {
                "description": str(meta.get("description", "")),
                "path": str(skill_file),
            }

    def list_skills(self) -> list[str]:
        return sorted(self._metadata.keys())

    def get_descriptions(self) -> str:
        lines = []
        for name in self.list_skills():
            description = self._metadata[name]["description"]
            lines.append(f"- {name}: {description}")
        return "\n".join(lines)

    def get_skill(self, name: str) -> Optional[Skill]:
        if name in self._cache:
            return self._cache[name]
        meta = self._metadata.get(name)
        if meta is None:
            return None

        path = Path(meta["path"])
        raw = path.read_text(encoding="utf-8")
        parsed_meta, body = self._split_frontmatter(raw)
        skill = Skill(
            name=str(parsed_meta.get("name", name)),
            description=str(parsed_meta.get("description", "")),
            body=body,
            path=path,
        )
        self._cache[name] = skill
        return skill

    def _split_frontmatter(self, text: str) -> tuple[Dict[str, str], str]:
        if not text.startswith("---"):
            return {}, text

        pieces = text.split("---", 2)
        if len(pieces) < 3:
            return {}, text

        frontmatter = pieces[1]
        body = pieces[2].lstrip("\n")
        metadata = yaml.safe_load(frontmatter) or {}
        if not isinstance(metadata, dict):
            metadata = {}
        return metadata, body
