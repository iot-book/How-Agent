"""Example bootstrap to import minimal_agents from local src checkout."""

from __future__ import annotations

import sys
from pathlib import Path


def bootstrap() -> None:
    src_path = Path(__file__).resolve().parents[3] / "src"
    src_str = str(src_path)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
