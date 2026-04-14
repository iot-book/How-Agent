from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Protocol

from ..tools.errors import ToolErrorCode
from ..tools.response import ToolResponse


@dataclass(slots=True)
class MCPToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]


class MCPClient(Protocol):
    def list_tools(self) -> list[MCPToolSpec]:
        ...

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResponse:
        ...


class InMemoryMCPClient:
    """A tiny MCP-like client for teaching and local tests."""

    def __init__(self):
        self._handlers: Dict[str, Callable[..., Any]] = {}
        self._specs: Dict[str, MCPToolSpec] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable[..., Any],
        *,
        parameters: Dict[str, Any] | None = None,
    ) -> None:
        schema = parameters or {"type": "object", "properties": {}, "required": []}
        self._handlers[name] = handler
        self._specs[name] = MCPToolSpec(name=name, description=description, parameters=schema)

    def list_tools(self) -> list[MCPToolSpec]:
        return [self._specs[name] for name in sorted(self._specs.keys())]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResponse:
        handler = self._handlers.get(name)
        if handler is None:
            return ToolResponse.error(ToolErrorCode.NOT_FOUND, f"MCP tool '{name}' not found.")

        try:
            result = handler(**arguments)
        except TypeError as exc:
            return ToolResponse.error(ToolErrorCode.INVALID_PARAM, str(exc))
        except Exception as exc:
            return ToolResponse.error(ToolErrorCode.EXECUTION_ERROR, str(exc))

        if isinstance(result, ToolResponse):
            return result
        if isinstance(result, dict):
            return ToolResponse.success(text=str(result.get("text", result)), data=result)
        return ToolResponse.success(text=str(result), data={"output": result})
