from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from utils.memory_utils import cosine_similarity, hash_embedding, tags_match, tokenize


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


class RAGManager:
    """RAG 管理器：支持文档入库、检索与高级策略扩展。"""

    SUPPORTED_SUFFIXES = {".md", ".txt", ".py", ".json", ".csv"}

    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size
        self._chunks: dict[str, DocumentChunk] = {}
        self._vectors: dict[str, list[float]] = {}
        # TODO: 可以考虑使用Chroma等向量数据库替代内存存储，以支持更大规模和更高效的检索。

    def add_file(
        self,
        file_path: str,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.suffix.lower() not in self.SUPPORTED_SUFFIXES:
            return 0

        text = path.read_text(encoding="utf-8", errors="ignore")
        chunks = self._split_text(text)
        now = datetime.now(timezone.utc).timestamp()

        for index, chunk_text in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            chunk = DocumentChunk(
                id=chunk_id,
                source=str(path),
                content=chunk_text,
                tags=tags or [],
                timestamp=now,
                metadata={
                    "chunk_index": index,
                    **(metadata or {}),
                },
            )
            self._chunks[chunk_id] = chunk
            self._vectors[chunk_id] = self._embed(chunk.content)

        return len(chunks)

    def add_directory(
        self,
        dir_path: str,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        root = Path(dir_path)
        if not root.exists() or not root.is_dir():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        total_chunks = 0
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in self.SUPPORTED_SUFFIXES:
                total_chunks += self.add_file(str(path), tags=tags, metadata=metadata)

        return total_chunks

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        tags: list[str] | None = None,
        use_mqe: bool = False,
        use_hyde: bool = False,
        use_rerank: bool = False,
    ) -> list[RetrievalResult]:
        expanded_queries = [query_text]

        if use_mqe:
            expanded_queries.extend(self.multi_query_expansion_placeholder(query_text))

        if use_hyde:
            hypothetical = self.hyde_placeholder(query_text)
            if hypothetical:
                expanded_queries.append(hypothetical)

        merged = self._merge_deduplicate(
            [self._retrieve_once(q, top_k=top_k, tags=tags) for q in expanded_queries]
        )

        merged.sort(key=lambda r: r.score, reverse=True)
        final_results = merged[:top_k]

        if use_rerank:
            final_results = self.rerank_placeholder(query_text, final_results)

        return final_results

    def rerank_placeholder(
        self,
        query_text: str,
        results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        """
        重排逻辑占位函数。

        常见实现：
        1) 使用 cross-encoder 对 (query, chunk) 打分。
        2) 或调用大模型评估每个片段的可回答性。
        """
        _ = query_text
        return results

    def multi_query_expansion_placeholder(self, query_text: str) -> list[str]:
        """
        多查询扩展（MQE）占位函数。

        可参考提示词：
        "把用户问题改写为 3 个语义等价但措辞不同的查询，
        每个查询强调不同关键词。"
        """
        _ = query_text
        return []

    def hyde_placeholder(self, query_text: str) -> str:
        """
        HyDE 占位函数。

        可参考提示词：
        "先写一段简洁、事实性强的假设答案，尽量包含领域术语，
        以便用于后续向量检索。"
        """
        _ = query_text
        return ""

    def _retrieve_once(
        self,
        query_text: str,
        top_k: int,
        tags: list[str] | None,
    ) -> list[RetrievalResult]:
        if not self._chunks:
            return []

        query_vec = self._embed(query_text)
        query_terms = set(tokenize(query_text))
        candidates: list[RetrievalResult] = []

        for chunk in self._chunks.values():
            if not tags_match(chunk.tags, tags):
                continue

            dense_score = cosine_similarity(query_vec, self._vectors.get(chunk.id, []))
            chunk_terms = set(tokenize(chunk.content))
            sparse_overlap = len(query_terms.intersection(chunk_terms)) / max(1, len(query_terms))
            score = 0.8 * dense_score + 0.2 * sparse_overlap

            candidates.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    source=chunk.source,
                    content=chunk.content,
                    score=score,
                    metadata=chunk.metadata,
                )
            )

        candidates.sort(key=lambda r: r.score, reverse=True)
        return candidates[:top_k]

    @staticmethod
    def _merge_deduplicate(result_lists: list[list[RetrievalResult]]) -> list[RetrievalResult]:
        best_by_chunk: dict[str, RetrievalResult] = {}
        for one_list in result_lists:
            for item in one_list:
                existing = best_by_chunk.get(item.chunk_id)
                if existing is None or item.score > existing.score:
                    best_by_chunk[item.chunk_id] = item
        return list(best_by_chunk.values())

    def _embed(self, text: str) -> list[float]:
        return hash_embedding(text, dim=128)

    def _split_text(self, text: str) -> list[str]:
        # 采用“按段优先”的简单分块策略，便于初学者理解。
        raw_parts = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not raw_parts:
            return []

        chunks: list[str] = []
        current = ""

        # 切分Chunk
        for part in raw_parts:
            if len(current) + len(part) + 2 <= self.chunk_size:
                current = f"{current}\n\n{part}".strip()
            else:
                if current:
                    chunks.append(current)
                if len(part) <= self.chunk_size:
                    current = part
                else:
                    # 对超长段落做硬切分，避免单块过大。
                    for i in range(0, len(part), self.chunk_size):
                        chunks.append(part[i : i + self.chunk_size])
                    current = ""

        if current:
            chunks.append(current)

        return chunks
