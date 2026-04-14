from __future__ import annotations

import sys
from pathlib import Path

# 设置项目路径，保证可以运行
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from memory import MemoryManager, MemoryType
from rag import RAGManager


def run_memory_demo() -> None:
    manager = MemoryManager()

    # 尝试添加一些记忆条目
    manager.add_memory(
        memory_type=MemoryType.WORKING,
        session_id="session_001",
        content="User prefers concise Python examples.",
        tags=["preference", "python"],
        importance=0.8,
    )
    manager.add_memory(
        memory_type=MemoryType.EPISODIC,
        session_id="session_001",
        content="Yesterday the user asked about vector databases and Chroma.",
        tags=["history", "rag"],
        importance=0.7,
    )
    manager.add_memory(
        memory_type=MemoryType.SEMANTIC,
        session_id="session_001",
        content="RAG often includes chunking, embedding, retrieval, and generation.",
        tags=["knowledge", "rag"],
        importance=0.9,
    )

    # 尝试查询记忆
    results = manager.query_all("How does RAG work?", top_k=3, tags=["rag"])
    for memory_type, entries in results.items():
        print(f"\n[{memory_type}]")
        for item in entries:
            print(f"score={item.score:.3f} | {item.memory.content}")


def run_rag_demo() -> None:
    rag = RAGManager(chunk_size=300)

    # 尝试加入一个文件
    loaded = rag.add_file(str(ROOT / "doc.md"), tags=["chapter08"])
    print(f"\nRAG loaded chunks: {loaded}")

    # 尝试查询知识库
    results = rag.query(
        query_text="What is HyDE in RAG?",
        top_k=3,
        tags=["chapter08"],
        use_mqe=False,
        use_hyde=False,
        use_rerank=False,
    )

    print("Top RAG results:")
    for i, r in enumerate(results, start=1):
        preview = r.content.replace("\n", " ")[:120]
        print(f"{i}. score={r.score:.3f} | {preview}...")


if __name__ == "__main__":
    run_memory_demo()
    run_rag_demo()
