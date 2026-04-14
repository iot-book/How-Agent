from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_example_module():
    examples_dir = Path(__file__).resolve().parents[1] / "examples"
    example_path = examples_dir / "teaching_full_capabilities_demo.py"
    examples_str = str(examples_dir)
    if examples_str not in sys.path:
        sys.path.insert(0, examples_str)

    spec = importlib.util.spec_from_file_location("teaching_full_capabilities_demo", example_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_full_capabilities_demo_runs_end_to_end():
    module = _load_example_module()

    answer = module.run_demo()

    assert answer == "标题：光合作用\n内容：植物把光能转成储存起来的化学能，并释放氧气。"
