from minimal_agents.tools import Tool, ToolParameter, ToolRegistry
from minimal_agents.tools.response import ToolResponse, ToolStatus
from minimal_agents.tools.errors import ToolErrorCode


class UpperTool(Tool):
    def __init__(self):
        super().__init__(name="upper", description="Uppercase a piece of text")

    def get_parameters(self):
        return [
            ToolParameter(
                name="text",
                type="string",
                description="text to uppercase",
                required=True,
            )
        ]

    def run(self, parameters):
        text = str(parameters.get("text", "")).strip()
        if not text:
            return ToolResponse.error(ToolErrorCode.INVALID_PARAM, "text is required")
        return ToolResponse.success(text=text.upper(), data={"value": text.upper()})


def test_registry_with_class_tool():
    registry = ToolRegistry()
    registry.register_tool(UpperTool())

    resp = registry.execute_tool("upper", {"text": "hello"})
    assert resp.status == ToolStatus.SUCCESS
    assert resp.data["value"] == "HELLO"


def test_registry_with_function_tool():
    registry = ToolRegistry()

    def greet(name: str) -> str:
        return f"hello {name}"

    registry.register_function(greet)
    resp = registry.execute_tool("greet", {"name": "teacher"})

    assert resp.status == ToolStatus.SUCCESS
    assert resp.data["output"] == "hello teacher"


def test_registry_not_found():
    registry = ToolRegistry()
    resp = registry.execute_tool("missing", {})

    assert resp.status == ToolStatus.ERROR
    assert resp.error_info["code"] == ToolErrorCode.NOT_FOUND


def test_openai_schema_export():
    registry = ToolRegistry()
    registry.register_tool(UpperTool())
    tools = registry.to_openai_tools()

    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "upper"
