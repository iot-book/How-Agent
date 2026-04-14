from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid


class MemoryType(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


@dataclass
class MemoryItem:
    """统一的记忆条目结构，供三类记忆模块共用。"""

    session_id: str
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tags: list[str] = field(default_factory=list)
    importance: float = 0.5
    timestamp: float = field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "content": self.content,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "importance": self.importance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryItem":
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            content=data["content"],
            timestamp=float(data["timestamp"]),
            tags=list(data.get("tags", [])),
            importance=float(data.get("importance", 0.5)),
        )


@dataclass
class ScoredMemory:
    memory: MemoryItem
    score: float
    relevance_score: float
    recency_score: float
    importance_score: float
