"""
自动评测脚本：对学生的记忆和RAG系统实现进行功能测试和打分。

运行方式：python -m pytest tests/test_grading.py -v
或：python tests/test_grading.py
"""

import sys
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 添加 code/src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memory.types.working_memory import WorkingMemoryManager
from memory.types.episodic_memory import EpisodicMemoryManager
from memory.types.semantic_memory import SemanticMemoryManager
from memory.manager import MemoryManager
from memory.models import MemoryItem, MemoryType
from rag.manager import RAGManager


def _new_episodic_manager() -> EpisodicMemoryManager:
    temp_dir = Path(tempfile.mkdtemp(prefix="grading_episodic_"))
    return EpisodicMemoryManager(storage_path=str(temp_dir / "episodic_memory.json"))


def _new_semantic_manager() -> SemanticMemoryManager:
    temp_dir = Path(tempfile.mkdtemp(prefix="grading_semantic_"))
    return SemanticMemoryManager(storage_path=str(temp_dir / "semantic_memory.json"))


def _new_memory_manager() -> MemoryManager:
    temp_dir = Path(tempfile.mkdtemp(prefix="grading_manager_"))
    return MemoryManager(
        working_memory=WorkingMemoryManager(),
        episodic_memory=EpisodicMemoryManager(storage_path=str(temp_dir / "episodic_memory.json")),
        semantic_memory=SemanticMemoryManager(storage_path=str(temp_dir / "semantic_memory.json")),
    )


class GradingTest:
    """评测测试类，记录各个功能的测试结果"""

    def __init__(self):
        self.scores = {}
        self.max_scores = {
            'working_memory_cleanup': 5,
            'working_memory_capacity': 5,
            'working_memory_query': 10,
            'episodic_memory_add': 8,
            'episodic_memory_query': 7,
            'semantic_memory_add': 8,
            'semantic_memory_query': 7,
            'manager_add': 5,
            'manager_update': 5,
            'manager_delete': 5,
            'manager_query_all': 5,
            'manager_forget': 5,
            'rag_split_text': 8,
            'rag_retrieve_once': 8,
            'rag_merge_deduplicate': 9,
        }

    def add_score(self, test_name: str, score: float, max_score: float = None):
        """记录测试成绩"""
        if max_score is None:
            max_score = self.max_scores.get(test_name, 10)
        self.scores[test_name] = (score, max_score)

    def get_total_score(self):
        """计算总分"""
        total = sum(score for score, _ in self.scores.values())
        max_total = sum(max_score for _, max_score in self.scores.values())
        return total, max_total

    def print_report(self):
        """打印评测报告"""
        print("\n" + "="*60)
        print("自动评测报告")
        print("="*60)

        # 按模块分组打印
        modules = {
            'Working Memory': [
                'working_memory_cleanup',
                'working_memory_capacity',
                'working_memory_query',
            ],
            'Episodic Memory': [
                'episodic_memory_add',
                'episodic_memory_query',
            ],
            'Semantic Memory': [
                'semantic_memory_add',
                'semantic_memory_query',
            ],
            'Memory Manager': [
                'manager_add',
                'manager_update',
                'manager_delete',
                'manager_query_all',
                'manager_forget',
            ],
            'RAG System': [
                'rag_split_text',
                'rag_retrieve_once',
                'rag_merge_deduplicate',
            ],
        }

        for module_name, tests in modules.items():
            module_score = 0
            module_max = 0
            print(f"\n{module_name}:")
            for test_name in tests:
                if test_name in self.scores:
                    score, max_score = self.scores[test_name]
                    module_score += score
                    module_max += max_score
                    status = "PASS" if score == max_score else "FAIL"
                    print(f"  [{status}] {test_name}: {score}/{max_score}")
            print(f"  小计: {module_score}/{module_max}")

        total, max_total = self.get_total_score()
        print(f"\n总分: {total}/{max_total} ({100*total/max_total:.1f}%)")
        print("="*60 + "\n")


def test_working_memory_cleanup():
    """测试工作记忆的过期清理"""
    test = GradingTest()
    try:
        mgr = WorkingMemoryManager(ttl_seconds=10)

        # 添加一个过期的记忆
        now = datetime.now(timezone.utc).timestamp()
        old_item = MemoryItem(
            id="old",
            session_id="test",
            content="old content",
            tags=[],
            importance=0.5,
            timestamp=now - 20,  # 20秒前，已过期（TTL=10秒）
        )
        mgr.add(old_item)

        # 添加一个未过期的记忆
        fresh_item = MemoryItem(
            id="fresh",
            session_id="test",
            content="fresh content",
            tags=[],
            importance=0.5,
            timestamp=now,
        )
        mgr.add(fresh_item)

        # 清理过期项
        removed = mgr.cleanup_expired()

        # 验证结果
        remaining = mgr.list_all()
        if removed >= 1 and len(remaining) >= 1 and any(m.id == "fresh" for m in remaining):
            test.add_score('working_memory_cleanup', 5)
            print("✓ working_memory_cleanup: PASS")
        else:
            test.add_score('working_memory_cleanup', 0)
            print(f"✗ working_memory_cleanup: FAIL (removed={removed}, remaining={len(remaining)})")
    except Exception as e:
        test.add_score('working_memory_cleanup', 0)
        print(f"✗ working_memory_cleanup: ERROR - {e}")

    return test


def test_working_memory_capacity():
    """测试工作记忆的容量限制"""
    test = GradingTest()
    try:
        mgr = WorkingMemoryManager(capacity=3)
        now = datetime.now(timezone.utc).timestamp()

        # 添加5个记忆，超过容量限制
        for i in range(5):
            item = MemoryItem(
                id=f"item_{i}",
                session_id="test",
                content=f"content {i}",
                tags=[],
                importance=0.5,
                timestamp=now + i,
            )
            mgr.add(item)

        # 检查是否只保留了3个
        remaining = mgr.list_all()
        if len(remaining) == 3:
            test.add_score('working_memory_capacity', 5)
            print("✓ working_memory_capacity: PASS")
        else:
            test.add_score('working_memory_capacity', 0)
            print(f"✗ working_memory_capacity: FAIL (expected 3, got {len(remaining)})")
    except Exception as e:
        test.add_score('working_memory_capacity', 0)
        print(f"✗ working_memory_capacity: ERROR - {e}")

    return test


def test_working_memory_query():
    """测试工作记忆的查询和打分"""
    test = GradingTest()
    try:
        mgr = WorkingMemoryManager()
        now = datetime.now(timezone.utc).timestamp()

        # 添加测试数据
        for i in range(3):
            item = MemoryItem(
                id=f"item_{i}",
                session_id="test",
                content=f"python machine learning",
                tags=[],
                importance=0.5 + i*0.1,
                timestamp=now - i*100,
            )
            mgr.add(item)

        # 查询
        results = mgr.query("python", top_k=2)

        # 检查返回的结果数量和得分
        if len(results) <= 2 and len(results) > 0:
            # 检查是否有打分（score不为0）
            has_scores = any(r.score > 0 for r in results)
            if has_scores:
                test.add_score('working_memory_query', 10)
                print("✓ working_memory_query: PASS")
            else:
                test.add_score('working_memory_query', 5)
                print("✓ working_memory_query: PARTIAL (no scores)")
        else:
            test.add_score('working_memory_query', 0)
            print(f"✗ working_memory_query: FAIL (returned {len(results)} items)")
    except Exception as e:
        test.add_score('working_memory_query', 0)
        print(f"✗ working_memory_query: ERROR - {e}")

    return test


def test_episodic_memory_add():
    """测试情节记忆的添加"""
    test = GradingTest()
    try:
        mgr = _new_episodic_manager()
        now = datetime.now(timezone.utc).timestamp()

        item = MemoryItem(
            id="test_id",
            session_id="test",
            content="test content",
            tags=["test"],
            importance=0.7,
            timestamp=now,
        )

        mgr.add(item)

        # 检查是否添加成功
        retrieved = mgr.get("test_id")
        if retrieved and retrieved.content == "test content":
            test.add_score('episodic_memory_add', 8)
            print("✓ episodic_memory_add: PASS")
        else:
            test.add_score('episodic_memory_add', 0)
            print("✗ episodic_memory_add: FAIL")
    except Exception as e:
        test.add_score('episodic_memory_add', 0)
        print(f"✗ episodic_memory_add: ERROR - {e}")

    return test


def test_episodic_memory_query():
    """测试情节记忆的查询"""
    test = GradingTest()
    try:
        mgr = _new_episodic_manager()
        now = datetime.now(timezone.utc).timestamp()

        # 添加测试数据
        for i in range(3):
            item = MemoryItem(
                id=f"item_{i}",
                session_id="test",
                content="deep learning neural network",
                tags=[],
                importance=0.5,
                timestamp=now,
            )
            mgr.add(item)

        # 查询
        results = mgr.query("deep learning", top_k=2)

        if len(results) > 0 and len(results) <= 2:
            test.add_score('episodic_memory_query', 7)
            print("✓ episodic_memory_query: PASS")
        else:
            test.add_score('episodic_memory_query', 0)
            print(f"✗ episodic_memory_query: FAIL (got {len(results)} results)")
    except Exception as e:
        test.add_score('episodic_memory_query', 0)
        print(f"✗ episodic_memory_query: ERROR - {e}")

    return test


def test_semantic_memory_add():
    """测试语义记忆的添加"""
    test = GradingTest()
    try:
        mgr = _new_semantic_manager()
        now = datetime.now(timezone.utc).timestamp()

        item = MemoryItem(
            id="sem_id",
            session_id="test",
            content="semantic knowledge",
            tags=["knowledge"],
            importance=0.8,
            timestamp=now,
        )

        mgr.add(item)

        retrieved = mgr.get("sem_id")
        if retrieved and retrieved.content == "semantic knowledge":
            test.add_score('semantic_memory_add', 8)
            print("✓ semantic_memory_add: PASS")
        else:
            test.add_score('semantic_memory_add', 0)
            print("✗ semantic_memory_add: FAIL")
    except Exception as e:
        test.add_score('semantic_memory_add', 0)
        print(f"✗ semantic_memory_add: ERROR - {e}")

    return test


def test_semantic_memory_query():
    """测试语义记忆的查询"""
    test = GradingTest()
    try:
        mgr = _new_semantic_manager()
        now = datetime.now(timezone.utc).timestamp()

        # 添加测试数据
        for i in range(2):
            item = MemoryItem(
                id=f"sem_{i}",
                session_id="test",
                content="artificial intelligence and machine learning",
                tags=[],
                importance=0.6,
                timestamp=now,
            )
            mgr.add(item)

        results = mgr.query("artificial intelligence", top_k=1)

        if len(results) > 0:
            test.add_score('semantic_memory_query', 7)
            print("✓ semantic_memory_query: PASS")
        else:
            test.add_score('semantic_memory_query', 0)
            print("✗ semantic_memory_query: FAIL")
    except Exception as e:
        test.add_score('semantic_memory_query', 0)
        print(f"✗ semantic_memory_query: ERROR - {e}")

    return test


def test_manager_add():
    """测试管理器的add_memory功能"""
    test = GradingTest()
    try:
        mgr = _new_memory_manager()

        result = mgr.add_memory(
            memory_type=MemoryType.EPISODIC,
            session_id="test",
            content="test content",
            tags=["test"],
            importance=0.6,
        )

        if result and result.content == "test content":
            test.add_score('manager_add', 5)
            print("✓ manager_add: PASS")
        else:
            test.add_score('manager_add', 0)
            print("✗ manager_add: FAIL")
    except Exception as e:
        test.add_score('manager_add', 0)
        print(f"✗ manager_add: ERROR - {e}")

    return test


def test_manager_update():
    """测试管理器的update_memory功能"""
    test = GradingTest()
    try:
        mgr = _new_memory_manager()

        item = mgr.add_memory(
            memory_type=MemoryType.SEMANTIC,
            session_id="test",
            content="original",
            tags=[],
            importance=0.5,
        )

        success = mgr.update_memory(
            memory_type=MemoryType.SEMANTIC,
            memory_id=item.id,
            content="updated",
        )

        if success:
            test.add_score('manager_update', 5)
            print("✓ manager_update: PASS")
        else:
            test.add_score('manager_update', 0)
            print("✗ manager_update: FAIL")
    except Exception as e:
        test.add_score('manager_update', 0)
        print(f"✗ manager_update: ERROR - {e}")

    return test


def test_manager_delete():
    """测试管理器的delete_memory功能"""
    test = GradingTest()
    try:
        mgr = _new_memory_manager()

        item = mgr.add_memory(
            memory_type=MemoryType.EPISODIC,
            session_id="test",
            content="to delete",
            tags=[],
            importance=0.5,
        )

        success = mgr.delete_memory(
            memory_type=MemoryType.EPISODIC,
            memory_id=item.id,
        )

        if success:
            test.add_score('manager_delete', 5)
            print("✓ manager_delete: PASS")
        else:
            test.add_score('manager_delete', 0)
            print("✗ manager_delete: FAIL")
    except Exception as e:
        test.add_score('manager_delete', 0)
        print(f"✗ manager_delete: ERROR - {e}")

    return test


def test_manager_query_all():
    """测试管理器的query_all功能"""
    test = GradingTest()
    try:
        mgr = _new_memory_manager()

        mgr.add_memory(
            memory_type=MemoryType.WORKING,
            session_id="test",
            content="working memory test",
            tags=[],
            importance=0.5,
        )

        results = mgr.query_all("test", top_k=1)

        if isinstance(results, dict) and MemoryType.WORKING in results:
            test.add_score('manager_query_all', 5)
            print("✓ manager_query_all: PASS")
        else:
            test.add_score('manager_query_all', 0)
            print("✗ manager_query_all: FAIL")
    except Exception as e:
        test.add_score('manager_query_all', 0)
        print(f"✗ manager_query_all: ERROR - {e}")

    return test


def test_manager_forget():
    """测试管理器的forget_low_importance功能"""
    test = GradingTest()
    try:
        mgr = _new_memory_manager()

        # 添加低重要性记忆（importance=0.1 < threshold=0.2）
        added_item = mgr.add_memory(
            memory_type=MemoryType.EPISODIC,
            session_id="test",
            content="unimportant",
            tags=[],
            importance=0.1,
        )

        # 添加高重要性记忆（importance=0.8 > threshold=0.2）
        mgr.add_memory(
            memory_type=MemoryType.EPISODIC,
            session_id="test",
            content="important",
            tags=[],
            importance=0.8,
        )

        removed = mgr.forget_low_importance(threshold=0.2)

        # 检查是否真的删除了低重要性的记忆，且删除数 >= 1
        if added_item and removed >= 1:
            test.add_score('manager_forget', 5)
            print("✓ manager_forget: PASS")
        else:
            test.add_score('manager_forget', 0)
            print(f"✗ manager_forget: FAIL (item added={added_item is not None}, removed={removed})")
    except Exception as e:
        test.add_score('manager_forget', 0)
        print(f"✗ manager_forget: ERROR - {e}")

    return test


def test_rag_split_text():
    """测试RAG的文本分块功能"""
    test = GradingTest()
    try:
        mgr = RAGManager(chunk_size=50)

        text = "Paragraph 1 with some content.\n\nParagraph 2 with more content here.\n\nParagraph 3."
        chunks = mgr._split_text(text)

        # 检查块大小是否合理
        valid = all(len(chunk) <= 50 for chunk in chunks) and len(chunks) > 0

        if valid:
            test.add_score('rag_split_text', 8)
            print("✓ rag_split_text: PASS")
        else:
            test.add_score('rag_split_text', 0)
            print(f"✗ rag_split_text: FAIL (chunks count={len(chunks)})")
    except Exception as e:
        test.add_score('rag_split_text', 0)
        print(f"✗ rag_split_text: ERROR - {e}")

    return test


def test_rag_retrieve_once():
    """测试RAG的单次检索功能"""
    test = GradingTest()
    try:
        mgr = RAGManager()

        # 添加文档
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Python is a programming language.\nMachine learning uses Python.")
            f.flush()
            temp_file = f.name

        try:
            mgr.add_file(temp_file)

            # 执行检索
            results = mgr._retrieve_once("Python programming", top_k=1, tags=None)

            if len(results) > 0:
                test.add_score('rag_retrieve_once', 8)
                print("✓ rag_retrieve_once: PASS")
            else:
                test.add_score('rag_retrieve_once', 0)
                print("✗ rag_retrieve_once: FAIL (no results)")
        finally:
            os.unlink(temp_file)
    except Exception as e:
        test.add_score('rag_retrieve_once', 0)
        print(f"✗ rag_retrieve_once: ERROR - {e}")

    return test


def test_rag_merge_deduplicate():
    """测试RAG的去重和合并功能"""
    test = GradingTest()
    try:
        from rag.manager import RetrievalResult

        # 创建重复和不同的结果
        result1 = RetrievalResult(
            chunk_id="chunk_1",
            source="file1",
            content="content 1",
            score=0.8,
        )
        result2 = RetrievalResult(
            chunk_id="chunk_1",
            source="file1",
            content="content 1",
            score=0.9,  # 同一个chunk但更高分
        )
        result3 = RetrievalResult(
            chunk_id="chunk_2",
            source="file2",
            content="content 2",
            score=0.7,
        )

        results = RAGManager._merge_deduplicate([[result1], [result2, result3]])

        # 应该保留chunk_1的高分版本和chunk_2
        if len(results) == 2:
            chunk_ids = {r.chunk_id for r in results}
            if chunk_ids == {"chunk_1", "chunk_2"}:
                test.add_score('rag_merge_deduplicate', 9)
                print("✓ rag_merge_deduplicate: PASS")
            else:
                test.add_score('rag_merge_deduplicate', 5)
                print("✓ rag_merge_deduplicate: PARTIAL")
        else:
            test.add_score('rag_merge_deduplicate', 0)
            print(f"✗ rag_merge_deduplicate: FAIL (got {len(results)} results)")
    except Exception as e:
        test.add_score('rag_merge_deduplicate', 0)
        print(f"✗ rag_merge_deduplicate: ERROR - {e}")

    return test


def run_all_tests():
    """运行所有测试"""
    tests = [
        test_working_memory_cleanup,
        test_working_memory_capacity,
        test_working_memory_query,
        test_episodic_memory_add,
        test_episodic_memory_query,
        test_semantic_memory_add,
        test_semantic_memory_query,
        test_manager_add,
        test_manager_update,
        test_manager_delete,
        test_manager_query_all,
        test_manager_forget,
        test_rag_split_text,
        test_rag_retrieve_once,
        test_rag_merge_deduplicate,
    ]

    combined_test = GradingTest()

    print("\n" + "="*60)
    print("自动评测开始")
    print("="*60 + "\n")

    for test_func in tests:
        result = test_func()
        # 合并结果
        for test_name, score_tuple in result.scores.items():
            combined_test.add_score(test_name, score_tuple[0], score_tuple[1])

    combined_test.print_report()

    total, max_total = combined_test.get_total_score()
    return total, max_total


if __name__ == "__main__":
    total, max_total = run_all_tests()
