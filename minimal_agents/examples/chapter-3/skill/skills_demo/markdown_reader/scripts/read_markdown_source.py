"""Read a Markdown source file and print a structured task brief."""

from __future__ import annotations

from pathlib import Path
import sys


def main() -> None:
    source_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "sample_source.md"
    content = source_path.read_text(encoding="utf-8")

    preview_lines = content.splitlines()[:8]
    print("## Source Brief")
    print(f"- Source path: {source_path}")
    print("- Read the source file before answering")
    print("- Extract the title and key sections first")
    print("- Source preview:")
    for line in preview_lines:
        print(f"  {line}")


if __name__ == "__main__":
    main()
