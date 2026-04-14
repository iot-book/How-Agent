from __future__ import annotations

from inspect import Parameter, Signature, _empty, signature
from typing import Any, Callable, Dict, Iterable, Optional

from .base import Tool, ToolParameter
from .errors import ToolErrorCode
from .response import ToolResponse


def _annotation_to_json_type(annotation: Any) -> str:
    mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        dict: "object",
        list: "array",
    }
    return mapping.get(annotation, "string")


class FunctionTool(Tool):
    def __init__(self, name: str, description: str, func: Callable[..., Any]):
        super().__init__(name=name, description=description)
        self._func = func
        self._signature: Signature = signature(func)

    def get_parameters(self) -> list[ToolParameter]:
        parameters: list[ToolParameter] = []
        for parameter in self._signature.parameters.values():
            if parameter.kind not in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY):
                continue
            param_type = _annotation_to_json_type(parameter.annotation)
            parameters.append(
                ToolParameter(
                    name=parameter.name,
                    type=param_type,
                    description=f"Parameter {parameter.name}",
                    required=parameter.default is _empty,
                )
            )
        return parameters

    def run(self, parameters: Dict[str, Any]) -> ToolResponse:
        if not isinstance(parameters, dict):
            params = list(self._signature.parameters.values())
            if len(params) == 1:
                parameters = {params[0].name: parameters}
            else:
                return ToolResponse.error(
                    ToolErrorCode.INVALID_PARAM,
                    "Function tool expects object parameters.",
                )

        try:
            result = self._func(**parameters)
        except TypeError as exc:
            return ToolResponse.error(ToolErrorCode.INVALID_PARAM, str(exc))
        except Exception as exc:
            return ToolResponse.error(ToolErrorCode.EXECUTION_ERROR, str(exc))

        if isinstance(result, ToolResponse):
            return result
        if isinstance(result, dict):
            text = str(result.get("text", result))
            return ToolResponse.success(text=text, data=result)
        return ToolResponse.success(text=str(result), data={"output": result})


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def register_function(
        self,
        func_or_name: Callable[..., Any] | str,
        description: Optional[str] = None,
        func: Optional[Callable[..., Any]] = None,
        *,
        name: Optional[str] = None,
    ) -> None:
        if callable(func_or_name):
            function = func_or_name
            tool_name = name or function.__name__
            tool_description = description or (function.__doc__ or "Function tool")
        else:
            if func is None:
                raise ValueError("func is required when first argument is a name")
            function = func
            tool_name = func_or_name
            tool_description = description or (function.__doc__ or "Function tool")

        self.register_tool(FunctionTool(tool_name, tool_description, function))

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def execute_tool(self, name: str, parameters: Dict[str, Any]) -> ToolResponse:
        tool = self.get_tool(name)
        if tool is None:
            return ToolResponse.error(
                ToolErrorCode.NOT_FOUND,
                f"Tool '{name}' not found.",
            )
        return tool.run(parameters)

    def to_openai_tools(self) -> list[Dict[str, Any]]:
        return [tool.to_openai_schema() for tool in self._tools.values()]
