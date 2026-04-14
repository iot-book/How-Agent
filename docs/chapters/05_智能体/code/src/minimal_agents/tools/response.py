from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import json


class ToolStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"


@dataclass(slots=True)
class ToolResponse:
    status: ToolStatus
    text: str
    data: Dict[str, Any] = field(default_factory=dict)
    error_info: Optional[Dict[str, str]] = None

    @classmethod
    def success(cls, text: str, data: Optional[Dict[str, Any]] = None) -> "ToolResponse":
        return cls(status=ToolStatus.SUCCESS, text=text, data=data or {})

    @classmethod
    def partial(cls, text: str, data: Optional[Dict[str, Any]] = None) -> "ToolResponse":
        return cls(status=ToolStatus.PARTIAL, text=text, data=data or {})

    @classmethod
    def error(cls, code: str, message: str) -> "ToolResponse":
        return cls(
            status=ToolStatus.ERROR,
            text=message,
            data={},
            error_info={"code": code, "message": message},
        )

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "status": self.status.value,
            "text": self.text,
            "data": self.data,
        }
        if self.error_info:
            payload["error"] = self.error_info
        return payload

    def to_message(self) -> str:
        if self.status == ToolStatus.SUCCESS and not self.data:
            return self.text
        return json.dumps(self.to_dict(), ensure_ascii=False)
