from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Optional, Protocol, Sequence
import json
import os
import uuid


@dataclass(slots=True)
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LLMResponse:
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: Any = None


class LLMBackend(Protocol):
    def complete(
        self,
        messages: Sequence[Dict[str, Any]],
        tools: Optional[Sequence[Dict[str, Any]]] = None,
        tool_choice: Any = "auto",
        **kwargs: Any,
    ) -> LLMResponse:
        ...


ScriptedOutput = LLMResponse | Dict[str, Any] | Callable[[Sequence[Dict[str, Any]], Optional[Sequence[Dict[str, Any]]]], LLMResponse | Dict[str, Any]]


class ScriptedLLMBackend:
    """Deterministic backend used by examples and tests."""

    def __init__(self, outputs: Iterable[ScriptedOutput]):
        self._outputs = list(outputs)
        self.calls: list[Dict[str, Any]] = []

    def complete(
        self,
        messages: Sequence[Dict[str, Any]],
        tools: Optional[Sequence[Dict[str, Any]]] = None,
        tool_choice: Any = "auto",
        **kwargs: Any,
    ) -> LLMResponse:
        self.calls.append(
            {
                "messages": list(messages),
                "tools": list(tools) if tools else None,
                "tool_choice": tool_choice,
                "kwargs": kwargs,
            }
        )
        if not self._outputs:
            raise RuntimeError("ScriptedLLMBackend has no output left.")

        current = self._outputs.pop(0)
        if callable(current):
            current = current(messages, tools)
        return _coerce_response(current)


def _coerce_response(payload: LLMResponse | Dict[str, Any]) -> LLMResponse:
    if isinstance(payload, LLMResponse):
        return payload

    tool_calls: list[ToolCall] = []
    for raw_call in payload.get("tool_calls", []):
        call_id = str(raw_call.get("id") or uuid.uuid4())
        tool_calls.append(
            ToolCall(
                id=call_id,
                name=raw_call["name"],
                arguments=dict(raw_call.get("arguments", {})),
            )
        )

    return LLMResponse(
        content=str(payload.get("content", "")),
        tool_calls=tool_calls,
        raw=payload,
    )


class HelloAgentsLLM:
    """LLM facade with pluggable backends and OpenAI-compatible fallback."""

    def __init__(
        self,
        backend: Optional[LLMBackend] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        self.backend = backend
        self.model = model or os.getenv("LLM_MODEL_ID", "gpt-4o-mini")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.temperature = temperature if temperature is not None else 0.2
        self._client = None

    def complete(
        self,
        messages: Sequence[Dict[str, Any]],
        tools: Optional[Sequence[Dict[str, Any]]] = None,
        tool_choice: Any = "auto",
        **kwargs: Any,
    ) -> LLMResponse:
        if self.backend is not None:
            return self.backend.complete(messages=messages, tools=tools, tool_choice=tool_choice, **kwargs)
        return self._complete_with_openai(messages=messages, tools=tools, tool_choice=tool_choice, **kwargs)

    def _ensure_openai_client(self):
        if self._client is not None:
            return self._client

        try:
            from openai import OpenAI
        except Exception as exc:
            raise RuntimeError(
                "openai package is required when backend is not provided"
            ) from exc

        init_kwargs: Dict[str, Any] = {}
        if self.api_key:
            init_kwargs["api_key"] = self.api_key
        if self.base_url:
            init_kwargs["base_url"] = self.base_url

        self._client = OpenAI(**init_kwargs)
        return self._client

    def _complete_with_openai(
        self,
        messages: Sequence[Dict[str, Any]],
        tools: Optional[Sequence[Dict[str, Any]]] = None,
        tool_choice: Any = "auto",
        **kwargs: Any,
    ) -> LLMResponse:
        client = self._ensure_openai_client()

        request: Dict[str, Any] = {
            "model": self.model,
            "messages": list(messages),
            "temperature": kwargs.get("temperature", self.temperature),
        }
        if tools:
            request["tools"] = list(tools)
            request["tool_choice"] = tool_choice

        raw = client.chat.completions.create(**request)
        message = raw.choices[0].message

        tool_calls: list[ToolCall] = []
        for raw_call in message.tool_calls or []:
            raw_args = raw_call.function.arguments or "{}"
            try:
                parsed_args = json.loads(raw_args)
            except json.JSONDecodeError:
                parsed_args = {"raw": raw_args}

            tool_calls.append(
                ToolCall(
                    id=raw_call.id or str(uuid.uuid4()),
                    name=raw_call.function.name,
                    arguments=parsed_args,
                )
            )

        return LLMResponse(
            content=message.content or "",
            tool_calls=tool_calls,
            raw=raw,
        )
