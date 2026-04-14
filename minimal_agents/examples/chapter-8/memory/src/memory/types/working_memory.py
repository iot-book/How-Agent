from __future__ import annotations

from datetime import datetime, timezone
from math import log

from ..models import MemoryItem, ScoredMemory
from utils.memory_utils import normalize_importance, recency_score, tags_match, tf_vector


class WorkingMemoryManager:
    """工作记忆管理器：容量受限，并支持 TTL 过期清理。"""

    def __init__(self, capacity: int = 20, ttl_seconds: int = 60 * 60):
        self.capacity = capacity
        self.ttl_seconds = ttl_seconds
        self._items: dict[str, MemoryItem] = {}

    def add(self, memory: MemoryItem) -> None:
        self._items[memory.id] = memory
        self.cleanup_expired()
        self._enforce_capacity()

    def update(self, memory_id: str, **updates: object) -> bool:
        item = self._items.get(memory_id)
        if not item:
            return False

        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return True

    def delete(self, memory_id: str) -> bool:
        return self._items.pop(memory_id, None) is not None

    def get(self, memory_id: str) -> MemoryItem | None:
        return self._items.get(memory_id)

    def list_all(self) -> list[MemoryItem]:
        return list(self._items.values())

    def cleanup_expired(self) -> int:
        now = datetime.now(timezone.utc).timestamp()
        # 找到所有过期的记忆ID
        removed_ids = [
            mid
            for mid, m in self._items.items()
            if now - m.timestamp > self.ttl_seconds
        ]
        for mid in removed_ids:
            self._items.pop(mid, None)
        return len(removed_ids)

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        tags: list[str] | None = None,
    ) -> list[ScoredMemory]:
        now = datetime.now(timezone.utc).timestamp()
        candidates = [m for m in self._items.values() if tags_match(m.tags, tags)]
        if not candidates:
            return []

        query_vec = tf_vector(query_text)
        scored: list[ScoredMemory] = []
        doc_freq = self._doc_frequency(candidates)

        for mem in candidates:
            mem_vec = tf_vector(mem.content)
            rel = self._tfidf_similarity(query_vec, mem_vec, doc_freq, len(candidates))
            rec = recency_score(now, mem.timestamp, half_life_seconds=max(300, self.ttl_seconds / 2))
            imp = normalize_importance(mem.importance)
            total = 0.5 * rel + 0.35 * rec + 0.15 * imp
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

    def _enforce_capacity(self) -> None:
        if len(self._items) <= self.capacity:
            return

        # 超过容量时，仅保留最近写入的记忆。
        sorted_items = sorted(
            self._items.values(),
            key=lambda m: m.timestamp,
            reverse=True,
        )
        keep = {m.id for m in sorted_items[: self.capacity]}
        self._items = {m.id: m for m in sorted_items if m.id in keep}

    @staticmethod
    def _doc_frequency(memories: list[MemoryItem]) -> dict[str, int]:
        df: dict[str, int] = {}
        for mem in memories:
            terms = set(tf_vector(mem.content).keys())
            for t in terms:
                df[t] = df.get(t, 0) + 1
        return df

    @staticmethod
    def _tfidf_similarity(
        query_tf: dict[str, float],
        doc_tf: dict[str, float],
        doc_freq: dict[str, int],
        n_docs: int,
    ) -> float:
        if not query_tf or not doc_tf:
            return 0.0

        score = 0.0
        for term, qv in query_tf.items():
            dv = doc_tf.get(term, 0.0)
            if dv <= 0.0:
                continue
            idf = log((n_docs + 1) / (1 + doc_freq.get(term, 0))) + 1.0
            score += qv * dv * idf
        return score
