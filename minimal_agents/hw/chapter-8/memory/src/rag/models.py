from dataclasses import dataclass, field
from typing import Any

@dataclass
class RetrievalResult:
    chunk_id: str
    source: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentChunk:
    id: str
    source: str
    content: str
    tags: list[str]
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)