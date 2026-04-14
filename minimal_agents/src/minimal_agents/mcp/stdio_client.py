from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..tools.errors import ToolErrorCode
from ..tools.response import ToolResponse
from .client import MCPToolSpec


class StdioMCPClient:
    """Connect to a local stdio MCP server via the official Python SDK."""

    def __init__(
        self,
        *,
        command: str,
        args: list[str] | None = None,
        cwd: str | Path | None = None,
        env: dict[str, str] | None = None,
    ):
        self.command = command
        self.args = args or []
        self.cwd = str(cwd) if cwd is not None else None
        self.env = env

    def list_tools(self) -> list[MCPToolSpec]:
        return self._run(self._list_tools_async)

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResponse:
        return self._run(lambda: self._call_tool_async(name, arguments))

    def _run(self, async_factory):
        try:
            import anyio
        except Exception as exc:
            raise RuntimeError("anyio package is required for StdioMCPClient") from exc

        return anyio.run(async_factory)

    async def _open_session(self):
        try:
            from mcp import ClientSession
            from mcp.client.stdio import StdioServerParameters, stdio_client
        except Exception as exc:
            raise RuntimeError("official mcp package is required for StdioMCPClient") from exc

        server = StdioServerParameters(
            command=self.command,
            args=self.args,
            cwd=self.cwd,
            env=self.env,
        )
        return ClientSession, stdio_client, server

    async def _list_tools_async(self) -> list[MCPToolSpec]:
        ClientSession, stdio_client, server = await self._open_session()
        async with stdio_client(server) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                result = await session.list_tools()
                return [
                    MCPToolSpec(
                        name=tool.name,
                        description=tool.description or "",
                        parameters=tool.inputSchema or {"type": "object", "properties": {}, "required": []},
                    )
                    for tool in result.tools
                ]

    async def _call_tool_async(self, name: str, arguments: Dict[str, Any]) -> ToolResponse:
        ClientSession, stdio_client, server = await self._open_session()
        async with stdio_client(server) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)
                if result.isError:
                    return ToolResponse.error(
                        ToolErrorCode.EXECUTION_ERROR,
                        self._result_to_text(result),
                    )

                data = result.structuredContent or {}
                return ToolResponse.success(
                    text=self._result_to_text(result),
                    data=data if isinstance(data, dict) else {"structured": data},
                )

    def _result_to_text(self, result: Any) -> str:
        content = getattr(result, "content", None) or []
        parts: list[str] = []
        for block in content:
            text = getattr(block, "text", None)
            if text:
                parts.append(str(text))
                continue
            parts.append(str(block))
        if parts:
            return "\n".join(parts)

        structured = getattr(result, "structuredContent", None)
        if structured is not None:
            return str(structured)
        return ""
