"""Teaching demo: MCP bridge with in-memory MCP client."""

from _bootstrap import bootstrap

bootstrap()

from minimal_agents import MinimalAgent, HelloAgentsLLM, ScriptedLLMBackend, ToolRegistry
from minimal_agents.mcp import InMemoryMCPClient, register_mcp_tools


def main() -> None:
    client = InMemoryMCPClient()
    client.register_tool(
        "echo",
        "Echo text",
        lambda text: {"text": f"mcp echo: {text}", "value": text},
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string", "description": "input"}},
            "required": ["text"],
        },
    )

    registry = ToolRegistry()
    register_mcp_tools(client, registry)

    llm = HelloAgentsLLM(backend=ScriptedLLMBackend([
        {
            "content": "using mcp",
            "tool_calls": [
                {"id": "m1", "name": "mcp_echo", "arguments": {"text": "hello"}},
            ],
        },
        {"content": "MCP tool worked."},
    ]))

    agent = MinimalAgent("mcp-demo", llm, tool_registry=registry)
    print(agent.run("call mcp echo"))


if __name__ == "__main__":
    main()
