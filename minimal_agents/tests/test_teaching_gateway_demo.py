from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_example_module():
    examples_dir = Path(__file__).resolve().parents[1] / "examples" / "chapter-7" / "gateway"
    example_path = examples_dir / "teaching_gateway_demo.py"
    examples_str = str(examples_dir)
    if examples_str not in sys.path:
        sys.path.insert(0, examples_str)

    spec = importlib.util.spec_from_file_location("teaching_gateway_demo", example_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_gateway_demo_routes_request_to_minimal_agent():
    module = _load_example_module()

    sample_path = Path(module.__file__).with_name("gateway_sample_note.md")
    gateway = module.SimpleGateway()
    gateway.register_agent("study-assistant", module.build_demo_agent(sample_path))

    response = gateway.dispatch(
        "study-assistant",
        module.GatewayRequest(
            channel="web",
            user_id="student-001",
            session_id="session-001",
            message="请读取 Markdown 并说明结构。",
        ),
    )

    assert response.channel == "web"
    assert response.agent_name == "study-assistant"
    assert "Minimal Agents Gateway Demo" in response.reply
    assert "Purpose / Key Points / Takeaway" in response.reply
