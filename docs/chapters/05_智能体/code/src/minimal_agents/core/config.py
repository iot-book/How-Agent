from dataclasses import dataclass


@dataclass(slots=True)
class AgentConfig:
    """Minimal runtime configuration for teaching agents."""

    max_history_messages: int = 20
    max_tool_iterations: int = 6
    max_react_steps: int = 8
    plan_max_steps: int = 5
    temperature: float = 0.2
