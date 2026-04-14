from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from ..models import MemoryItem, ScoredMemory
from utils.memory_utils import cosine_similarity, hash_embedding, normalize_importance, recency_score, tags_match, tokenize


class SemanticMemoryManager:
    """语义记忆管理器：存储抽象知识，并预留高级语义检索扩展点。"""

    def __init__(self, storage_path: str = "./data/semantic_memory.json"):
        self.storage_path = Path(storage_path)
        self._items: dict[str, MemoryItem] = {}
        self._vectors: dict[str, list[float]] = {}
        self._load()

    def add(self, memory: MemoryItem) -> None:
        self._items[memory.id] = memory
        self._vectors[memory.id] = self.embed(memory.content)
        self._save()

        # TODO: 语义记忆可以考虑采用基于图的实体-关系模型等，以支持更复杂的知识表示和推理。

    def update(self, memory_id: str, **updates: object) -> bool:
        item = self._items.get(memory_id)
        if not item:
            return False

        # 更新属性，如果内容被修改则需要重新计算向量
        content_changed = False
        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)
                if key == "content":
                    content_changed = True

        if content_changed:
            self._vectors[memory_id] = self.embed(item.content)

        self._save()
        return True

    def delete(self, memory_id: str) -> bool:
        removed = self._items.pop(memory_id, None) is not None
        self._vectors.pop(memory_id, None)
        if removed:
            self._save()
        return removed

    def get(self, memory_id: str) -> MemoryItem | None:
        return self._items.get(memory_id)

    def list_all(self) -> list[MemoryItem]:
        return list(self._items.values())

    def embed(self, text: str) -> list[float]:
        # 使用紧凑向量；实际使用建议替换为更强的 embedding 模型。
        return hash_embedding(text, dim=128)

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        tags: list[str] | None = None,
    ) -> list[ScoredMemory]:
        now = datetime.now(timezone.utc).timestamp()
        query_vec = self.embed(query_text)
        query_terms = set(tokenize(query_text))

        scored: list[ScoredMemory] = []
        for mem in self._items.values():
            if not tags_match(mem.tags, tags):
                continue

            rel = cosine_similarity(query_vec, self._vectors.get(mem.id, []))
            # 额外加入少量关键词重叠奖励，便于初学者观察到“词面匹配”的影响。
            mem_terms = set(tokenize(mem.content))
            overlap = len(query_terms.intersection(mem_terms)) / max(1, len(query_terms))
            rel = min(1.0, 0.85 * rel + 0.15 * overlap)

            rec = recency_score(now, mem.timestamp, half_life_seconds=30 * 24 * 3600)
            imp = normalize_importance(mem.importance)
            total = 0.65 * rel + 0.25 * imp + 0.10 * rec

            scored.append(
                ScoredMemory(
                    memory=mem,
                    score=total,
                    relevance_score=rel,
                    recency_score=rec,
                    importance_score=imp,
                )
            )

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]

    def advanced_semantic_search_placeholder(self, query_text: str) -> list[str]:
        """
        更高级语义检索的占位函数。

        可选实现方式：
        1) 向量召回后接入 cross-encoder 重排。
        2) 结合知识图谱扩展相关概念再检索。
        3) 采用混合检索（BM25 + 稠密向量融合）。
        """
        _ = query_text
        return []

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "items": [m.to_dict() for m in self._items.values()],
            "vectors": self._vectors,
        }
        self.storage_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load(self) -> None:
        if not self.storage_path.exists():
            return

        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        self._items = {
            raw["id"]: MemoryItem.from_dict(raw)
            for raw in data.get("items", [])
        }
        self._vectors = {
            k: [float(v) for v in values]
            for k, values in data.get("vectors", {}).items()
        }
