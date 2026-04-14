from __future__ import annotations

from typing import Dict, Any

from .client import MCPClient, MCPToolSpec
from ..tools.base import Tool, ToolParameter
from ..tools.registry import ToolRegistry
from ..tools.response import ToolResponse


class MCPToolAdapter(Tool):
    def __init__(
        self,
        client: MCPClient,
        spec: MCPToolSpec,
        *,
        local_name: str | None = None,
    ):
        self.client = client
        self.remote_name = spec.name
        self.spec = spec
        super().__init__(name=local_name or spec.name, description=spec.description)

    def get_parameters(self) -> list[ToolParameter]:
        schema = self.spec.parameters or {}
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        params: list[ToolParameter] = []
        for name, prop in properties.items():
            params.append(
                ToolParameter(
                    name=name,
                    type=str(prop.get("type", "string")),
                    description=str(prop.get("description", f"Parameter {name}")),
                    required=name in required,
                )
            )
        return params

    def run(self, parameters: Dict[str, Any]) -> ToolResponse:
        return self.client.call_tool(self.remote_name, parameters)


def register_mcp_tools(client: MCPClient, registry: ToolRegistry, *, prefix: str = "mcp_") -> None:
    for spec in client.list_tools():
        registry.register_tool(MCPToolAdapter(client, spec, local_name=f"{prefix}{spec.name}"))
