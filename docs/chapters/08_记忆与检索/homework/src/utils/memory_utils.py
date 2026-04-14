from __future__ import annotations

import math
import re
from collections import Counter


def normalize_importance(importance: float) -> float:
    return max(0.0, min(1.0, importance))


def tokenize(text: str) -> list[str]:
    # 仅保留简单词元，便于初学者理解且结果稳定。
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def hash_embedding(text: str, dim: int = 64) -> list[float]:
    # 当没有可用向量模型时，使用轻量哈希向量做教学演示。
    vec = [0.0] * dim
    for token in tokenize(text):
        idx = hash(token) % dim
        vec[idx] += 1.0

    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def tf_vector(text: str) -> dict[str, float]:
    words = tokenize(text)
    if not words:
        return {}
    cnt = Counter(words)
    total = float(len(words))
    return {w: c / total for w, c in cnt.items()}


def recency_score(now_ts: float, memory_ts: float, half_life_seconds: float) -> float:
    age = max(0.0, now_ts - memory_ts)
    if half_life_seconds <= 0:
        return 1.0
    return math.exp(-math.log(2) * age / half_life_seconds)


def tags_match(memory_tags: list[str], required_tags: list[str] | None) -> bool:
    if not required_tags:
        return True
    mem_set = set(memory_tags)
    required_set = set(required_tags)
    return bool(mem_set.intersection(required_set))
