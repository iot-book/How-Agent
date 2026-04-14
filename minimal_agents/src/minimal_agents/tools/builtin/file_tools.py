from __future__ import annotations

from pathlib import Path

from ..base import Tool, ToolParameter
from ..errors import ToolErrorCode
from ..response import ToolResponse


class ReadTool(Tool):
    def __init__(self):
        super().__init__(name="read_file", description="Read text from a file.")

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(name="path", type="string", description="File path", required=True),
        ]

    def run(self, parameters: dict) -> ToolResponse:
        path = Path(str(parameters.get("path", "")))
        if not path.exists():
            return ToolResponse.error(ToolErrorCode.NOT_FOUND, f"File not found: {path}")
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as exc:
            return ToolResponse.error(ToolErrorCode.EXECUTION_ERROR, str(exc))
        return ToolResponse.success(text=content, data={"path": str(path), "size": len(content)})


class WriteTool(Tool):
    def __init__(self):
        super().__init__(name="write_file", description="Write text into a file.")

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(name="path", type="string", description="File path", required=True),
            ToolParameter(name="content", type="string", description="File content", required=True),
        ]

    def run(self, parameters: dict) -> ToolResponse:
        path = Path(str(parameters.get("path", "")))
        content = str(parameters.get("content", ""))
        if not path:
            return ToolResponse.error(ToolErrorCode.INVALID_PARAM, "Parameter 'path' is required.")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except Exception as exc:
            return ToolResponse.error(ToolErrorCode.EXECUTION_ERROR, str(exc))
        return ToolResponse.success(text=f"Wrote {len(content)} chars to {path}", data={"path": str(path)})


class EditTool(Tool):
    def __init__(self):
        super().__init__(name="edit_file", description="Replace text in a file once.")

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(name="path", type="string", description="File path", required=True),
            ToolParameter(name="old", type="string", description="Text to replace", required=True),
            ToolParameter(name="new", type="string", description="Replacement text", required=True),
        ]

    def run(self, parameters: dict) -> ToolResponse:
        path = Path(str(parameters.get("path", "")))
        old = str(parameters.get("old", ""))
        new = str(parameters.get("new", ""))
        if not path.exists():
            return ToolResponse.error(ToolErrorCode.NOT_FOUND, f"File not found: {path}")
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:
            return ToolResponse.error(ToolErrorCode.EXECUTION_ERROR, str(exc))

        if old not in text:
            return ToolResponse.error(ToolErrorCode.INVALID_PARAM, "Target text not found.")

        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        return ToolResponse.success(text=f"Updated {path}", data={"path": str(path)})
