from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List

from .response import ToolResponse


def tool_action(name: str | None = None, description: str | None = None):
    """Decorator kept for teaching compatibility."""

    def _wrap(func):
        func._tool_action_name = name
        func._tool_action_description = description
        return func

    return _wrap


@dataclass(slots=True)
class ToolParameter:
    name: str
    type: str
    description: str
    required: bool = True


class Tool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, parameters: Dict[str, Any]) -> ToolResponse:
        ...

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        ...

    def to_openai_schema(self) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}
        required: List[str] = []
        for parameter in self.get_parameters():
            properties[parameter.name] = {
                "type": parameter.type,
                "description": parameter.description,
            }
            if parameter.required:
                required.append(parameter.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
