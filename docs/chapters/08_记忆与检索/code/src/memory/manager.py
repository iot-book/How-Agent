from __future__ import annotations

from datetime import datetime, timezone

from .models import MemoryItem, MemoryType, ScoredMemory
from .types import EpisodicMemoryManager, SemanticMemoryManager, WorkingMemoryManager
from utils.memory_utils import normalize_importance


class MemoryManager:
    """统一记忆管理器：对三类记忆提供一致的增删改查接口。"""

    def __init__(
        self,
        working_memory: WorkingMemoryManager | None = None,
        episodic_memory: EpisodicMemoryManager | None = None,
        semantic_memory: SemanticMemoryManager | None = None,
    ):
        self.working_memory = working_memory or WorkingMemoryManager()
        self.episodic_memory = episodic_memory or EpisodicMemoryManager()
        self.semantic_memory = semantic_memory or SemanticMemoryManager()

    def add_memory(
        self,
        memory_type: MemoryType,
        session_id: str,
        content: str,
        tags: list[str] | None = None,
        importance: float = 0.5,
    ) -> MemoryItem:
        # 构造记忆条目
        memory = MemoryItem(
            session_id=session_id,
            content=content,
            tags=tags or [],
            importance=normalize_importance(importance),
            timestamp=datetime.now(timezone.utc).timestamp(),
        )

        # 存入对应的记忆模块
        module = self._get_module(memory_type)
        module.add(memory)
        return memory

    def update_memory(
        self,
        memory_type: MemoryType,
        memory_id: str,
        **updates: object,
    ) -> bool:
        if "importance" in updates:
            updates["importance"] = normalize_importance(float(updates["importance"]))
        module = self._get_module(memory_type)
        return module.update(memory_id, **updates)

    def delete_memory(self, memory_type: MemoryType, memory_id: str) -> bool:
        module = self._get_module(memory_type)
        return module.delete(memory_id)

    def get_memory(self, memory_type: MemoryType, memory_id: str) -> MemoryItem | None:
        module = self._get_module(memory_type)
        return module.get(memory_id)

    def query_memory(
        self,
        memory_type: MemoryType,
        query_text: str,
        top_k: int = 5,
        tags: list[str] | None = None,
    ) -> list[ScoredMemory]:
        module = self._get_module(memory_type)
        return module.query(query_text=query_text, top_k=top_k, tags=tags)

    def query_all(
        self,
        query_text: str,
        top_k: int = 5,
        tags: list[str] | None = None,
    ) -> dict[MemoryType, list[ScoredMemory]]:
        return {
            MemoryType.WORKING: self.working_memory.query(query_text, top_k=top_k, tags=tags),
            MemoryType.EPISODIC: self.episodic_memory.query(query_text, top_k=top_k, tags=tags),
            MemoryType.SEMANTIC: self.semantic_memory.query(query_text, top_k=top_k, tags=tags),
        }

    def run_maintenance(self) -> dict[str, int]:
        """
        执行例行维护任务。

        当前包含：
        1) 清理工作记忆中过期项。
        2) 执行重要性重平衡（占位策略）。
        """
        removed_working = self.working_memory.cleanup_expired()
        updated_importance = self.rebalance_priorities()
        return {
            "removed_working": removed_working,
            "updated_importance": updated_importance,
        }

    def rebalance_priorities(self) -> int:
        """
        调整记忆重要性分数。

        生产环境可调用大模型，结合对话目标、近期性、任务完成情况
        来重新估计重要性。
        """
        updated = 0
        for m in self.working_memory.list_all():
            new_score = self.estimate_importance_placeholder(m)
            if abs(new_score - m.importance) > 1e-6:
                self.working_memory.update(m.id, importance=new_score)
                updated += 1

        for manager in (self.episodic_memory, self.semantic_memory):
            for m in manager.list_all():
                new_score = self.estimate_importance_placeholder(m)
                if abs(new_score - m.importance) > 1e-6:
                    manager.update(m.id, importance=new_score)
                    updated += 1

        return updated

    def forget_low_importance(self, threshold: float = 0.15) -> int:
        """删除长期记忆中重要性过低的条目。"""
        threshold = normalize_importance(threshold)
        removed = 0

        for manager in (self.episodic_memory, self.semantic_memory):
            to_delete = [m.id for m in manager.list_all() if m.importance < threshold]
            for memory_id in to_delete:
                if manager.delete(memory_id):
                    removed += 1

        return removed

    @staticmethod
    def estimate_importance_placeholder(memory: MemoryItem) -> float:
        """
        基于大模型的重要性评估占位函数。

        可参考的提示词：
        "给定记忆内容、用户目标和近期上下文，请给出 [0,1] 的重要性分数，
        用于后续决策。"
        """
        # 当前版本不改变分数，直接返回当前值。
        return normalize_importance(memory.importance)

    def _get_module(
        self,
        memory_type: MemoryType,
    ) -> WorkingMemoryManager | EpisodicMemoryManager | SemanticMemoryManager:
        if memory_type == MemoryType.WORKING:
            return self.working_memory
        if memory_type == MemoryType.EPISODIC:
            return self.episodic_memory
        if memory_type == MemoryType.SEMANTIC:
            return self.semantic_memory
        raise ValueError(f"Unsupported memory type: {memory_type}")
