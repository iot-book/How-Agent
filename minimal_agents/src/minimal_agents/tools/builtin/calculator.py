from __future__ import annotations

import ast
import math
import operator
from typing import Any

from ..base import Tool, ToolParameter
from ..errors import ToolErrorCode
from ..response import ToolResponse


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_ALLOWED_FUNCS = {
    "sqrt": math.sqrt,
    "abs": abs,
    "round": round,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
}

_CONSTANTS = {"pi": math.pi, "e": math.e}


class _Evaluator(ast.NodeVisitor):
    def visit_Expression(self, node: ast.Expression) -> Any:  # noqa: N802
        return self.visit(node.body)

    def visit_BinOp(self, node: ast.BinOp) -> Any:  # noqa: N802
        op_type = type(node.op)
        if op_type not in _BIN_OPS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        return _BIN_OPS[op_type](self.visit(node.left), self.visit(node.right))

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:  # noqa: N802
        op_type = type(node.op)
        if op_type not in _UNARY_OPS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return _UNARY_OPS[op_type](self.visit(node.operand))

    def visit_Call(self, node: ast.Call) -> Any:  # noqa: N802
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct function calls are allowed")
        func_name = node.func.id
        if func_name not in _ALLOWED_FUNCS:
            raise ValueError(f"Function '{func_name}' is not allowed")
        func = _ALLOWED_FUNCS[func_name]
        args = [self.visit(arg) for arg in node.args]
        return func(*args)

    def visit_Name(self, node: ast.Name) -> Any:  # noqa: N802
        if node.id not in _CONSTANTS:
            raise ValueError(f"Unknown name: {node.id}")
        return _CONSTANTS[node.id]

    def visit_Constant(self, node: ast.Constant) -> Any:  # noqa: N802
        if not isinstance(node.value, (int, float)):
            raise ValueError("Only numeric constants are allowed")
        return node.value

    def generic_visit(self, node):  # noqa: D401
        raise ValueError(f"Unsupported syntax: {type(node).__name__}")


def _safe_eval(expression: str) -> float:
    parsed = ast.parse(expression, mode="eval")
    value = _Evaluator().visit(parsed)
    return float(value)


class CalculatorTool(Tool):
    def __init__(self):
        super().__init__(name="calculator", description="Evaluate a math expression safely.")

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="expression",
                type="string",
                description="Math expression, e.g. '2 + 3 * 4'.",
                required=True,
            )
        ]

    def run(self, parameters: dict) -> ToolResponse:
        expression = str(parameters.get("expression") or parameters.get("input") or "").strip()
        if not expression:
            return ToolResponse.error(
                ToolErrorCode.INVALID_PARAM,
                "Parameter 'expression' is required.",
            )

        try:
            result = _safe_eval(expression)
        except Exception as exc:
            return ToolResponse.error(ToolErrorCode.EXECUTION_ERROR, str(exc))

        return ToolResponse.success(
            text=f"{expression} = {result}",
            data={"expression": expression, "result": result},
        )
