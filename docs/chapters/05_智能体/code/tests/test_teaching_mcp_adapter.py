from minimal_agents.mcp import InMemoryMCPClient, register_mcp_tools
from minimal_agents.tools import ToolRegistry
from minimal_agents.tools.response import ToolStatus


def test_mcp_tool_registration_and_call():
    client = InMemoryMCPClient()
    client.register_tool(
        "echo",
        "Echo input",
        lambda text: {"text": f"echo: {text}", "value": text},
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string", "description": "input text"}},
            "required": ["text"],
        },
    )

    registry = ToolRegistry()
    register_mcp_tools(client, registry)

    assert "mcp_echo" in registry.list_tools()
    response = registry.execute_tool("mcp_echo", {"text": "hello"})

    assert response.status == ToolStatus.SUCCESS
    assert response.data["value"] == "hello"
