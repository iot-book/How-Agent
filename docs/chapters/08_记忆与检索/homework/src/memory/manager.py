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
        """添加一条新的记忆项。

        TODO: 实现记忆条目创建和存储逻辑。
        需要：
        1. 创建MemoryItem实例，包含session_id、content、tags、importance、timestamp
        2. 标准化importance分数（使用normalize_importance函数）
        3. 获取对应的记忆模块（使用_get_module方法）
        4. 将记忆项添加到对应模块（调用module.add方法）
        5. 返回创建的记忆项
        """
        # TODO: 实现存储逻辑
        return None  # type: ignore

    def update_memory(
        self,
        memory_type: MemoryType,
        memory_id: str,
        **updates: object,
    ) -> bool:
        """更新指定记忆项的属性。

        TODO: 实现记忆更新逻辑。
        需要：
        1. 如果updates中包含"importance"，需要标准化该字段（使用normalize_importance函数）
        2. 获取对应的记忆模块（使用_get_module方法）
        3. 调用module.update方法进行更新
        4. 返回更新是否成功
        """
        # TODO: 实现更新逻辑
        return False

    def delete_memory(self, memory_type: MemoryType, memory_id: str) -> bool:
        """删除指定的记忆项。

        TODO: 实现记忆删除逻辑。
        需要：
        1. 获取对应的记忆模块（使用_get_module方法）
        2. 调用module.delete方法进行删除
        3. 返回删除是否成功
        """
        # TODO: 实现删除逻辑
        return False

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
        """查询所有三类记忆，返回合并的结果。

        TODO: 实现并行查询逻辑。
        需要：
        1. 分别从working_memory、episodic_memory、semantic_memory中查询
        2. 每个模块调用query方法，传入query_text、top_k、tags
        3. 返回格式为字典，key为MemoryType，value为ScoredMemory列表
        """
        # TODO: 实现查询逻辑
        return {}

    def forget_low_importance(self, threshold: float = 0.15) -> int:
        """删除长期记忆中重要性过低的条目。

        TODO: 实现遗忘机制。
        需要：
        1. 标准化threshold（使用normalize_importance函数）
        2. 遍历episodic_memory和semantic_memory（不包括working_memory）
        3. 对每个管理器，找到所有importance < threshold的项
        4. 删除这些项，并统计删除总数
        5. 返回删除的总数
        """
        # TODO: 实现遗忘逻辑
        return 0

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
