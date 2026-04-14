from minimal_agents.core import AgentConfig, Message
from minimal_agents.core.llm import HelloAgentsLLM, ScriptedLLMBackend


def test_message_to_dict():
    msg = Message(role="user", content="hello", name="alice", tool_call_id="x")
    payload = msg.to_dict()
    assert payload["role"] == "user"
    assert payload["name"] == "alice"
    assert payload["tool_call_id"] == "x"


def test_config_defaults():
    config = AgentConfig()
    assert config.max_tool_iterations > 0
    assert config.max_react_steps >= config.max_tool_iterations


def test_scripted_llm_backend():
    backend = ScriptedLLMBackend([{"content": "ok"}])
    llm = HelloAgentsLLM(backend=backend)
    resp = llm.complete([{"role": "user", "content": "hi"}])
    assert resp.content == "ok"
    assert resp.tool_calls == []
