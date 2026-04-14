"""Helper tools for the chapter 7 gateway teaching demo."""

from __future__ import annotations

from pathlib import Path


def read_markdown_overview(path: str) -> dict:
    """Read a Markdown file and return a small structured summary."""
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")

    title = "Untitled"
    headings: list[str] = []
    bullet_count = 0

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
        elif stripped.startswith("## "):
            headings.append(stripped[3:].strip())
        elif stripped.startswith("- "):
            bullet_count += 1

    return {
        "text": f"Read markdown file: {file_path.name}",
        "path": file_path.name,
        "title": title,
        "headings": headings,
        "bullet_count": bullet_count,
    }
