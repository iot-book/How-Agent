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
        """添加语义记忆项，并计算向量并保存。

        TODO: 实现内存存储和向量存储逻辑。
        需要：
        1. 将memory存储到 self._items[memory.id]
        2. 计算内容的向量表示（使用self.embed方法），存储到 self._vectors[memory.id]
        3. 调用 self._save() 持久化到文件

        提示：语义记忆可以考虑采用基于图的实体-关系模型等，以支持更复杂的知识表示和推理。
        """
        # TODO: 实现存储逻辑

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
        """查询语义记忆，返回与query_text最相关的前top_k项。

        TODO: 实现向量相似度 + 词面重叠奖励 + 重要性与时间衰减加权逻辑。

        步骤：
        1. 获取当前时间戳 now
        2. 生成query_text的向量表示（使用self.embed方法）
        3. 对query_text分词（使用tokenize函数）
        4. 筛选满足tag条件的候选记忆（使用tags_match函数）
        5. 对每个候选记忆计算：
           - dense_rel: 向量余弦相似度（使用cosine_similarity函数）
           - overlap: 词面重叠比例（query_terms 与 mem_terms 交集 / query_terms长度）
           - rel: 组合相关度 = min(1.0, 0.85*dense_rel + 0.15*overlap)
           - rec: 时间衰减分数（使用recency_score函数，half_life_seconds=30*24*3600）
           - imp: 标准化重要性（使用normalize_importance函数）
           - total: 加权合成 = 0.65*rel + 0.25*imp + 0.10*rec
        6. 按total分数排序降序，返回前top_k项
        """
        now = datetime.now(timezone.utc).timestamp()
        query_vec = self.embed(query_text)
        query_terms = set(tokenize(query_text))

        scored: list[ScoredMemory] = []
        for mem in self._items.values():
            if not tags_match(mem.tags, tags):
                continue
            # TODO: 实现打分逻辑

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]

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
