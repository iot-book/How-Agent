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
        # self.cleanup_expired()  # 为了测试需要，暂时注释掉过期清理；实际使用时建议开启
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
        """清理超过TTL的过期记忆项。

        TODO: 实现基于 datetime.now(timezone.utc).timestamp() 和 self.ttl_seconds 的过期检测逻辑。
        需要：
        1. 获取当前时间戳
        2. 找到所有满足 (now - timestamp > ttl_seconds) 的记忆ID
        3. 删除这些过期项
        4. 返回删除的数量
        """
        now = datetime.now(timezone.utc).timestamp()
        # TODO: 实现删除逻辑
        return 0

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        tags: list[str] | None = None,
    ) -> list[ScoredMemory]:
        """查询工作记忆，返回与query_text最相关的前top_k项。

        TODO: 实现TF-IDF相似度 + 时间衰减 + 重要性加权的综合打分逻辑。

        步骤：
        1. 获取当前时间戳 now
        2. 筛选满足tag条件的候选记忆（使用tags_match函数）
        3. 对query_text进行TF词向量化（使用tf_vector函数）
        4. 计算文档频率（doc_freq）用于IDF
        5. 对每个候选记忆计算：
           - rel: TF-IDF相似度（使用_tfidf_similarity方法）
           - rec: 时间衰减分数（使用recency_score函数，half_life=max(300, ttl/2)）
           - imp: 标准化重要性（使用normalize_importance函数）
           - total: 加权合成 = 0.5*rel + 0.35*rec + 0.15*imp
        6. 按total分数排序降序，返回前top_k项
        """
        now = datetime.now(timezone.utc).timestamp()
        candidates = [m for m in self._items.values() if tags_match(m.tags, tags)]
        if not candidates:
            return []

        query_vec = tf_vector(query_text)
        scored: list[ScoredMemory] = []
        doc_freq = self._doc_frequency(candidates)

        for mem in candidates:
            mem_vec = tf_vector(mem.content)
            # TODO: 实现打分逻辑

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]

    def _enforce_capacity(self) -> None:
        """当记忆数超过容量限制时，保留最近的N项，删除其他的。

        TODO: 实现容量强制策略。
        需要：
        1. 检查是否超过self.capacity
        2. 如果超过，用 timestamp 降序排列所有记忆
        3. 保留前 self.capacity 个（最新的）
        4. 删除其他的
        """
        if len(self._items) <= self.capacity:
            return
        # TODO: 实现保留最新记忆的逻辑

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
