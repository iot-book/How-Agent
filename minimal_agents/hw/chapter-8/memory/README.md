# 记忆与检索系统 - 作业说明

## 一、简介

本作业要求同学们实现一个完整的**记忆管理系统**和**RAG（Retrieval-Augmented Generation）检索系统**。

系统分为两个主要模块：
- **Memory System**：支持三种类型的记忆（工作记忆、情节记忆、语义记忆）
- **RAG System**：支持文档检索和召回

## 二、作业要求

本作业总分为 **100分**，分为两个部分：

### Part 1：记忆系统实现 （75分）

#### 1.1 工作记忆（Working Memory）【20分】

文件：`src/memory/types/working_memory.py`

**要求填空的函数：**

- **`cleanup_expired()`** (5分) - 清理过期记忆
  - 基于 `timestamp` 和 `ttl_seconds` 删除过期项
  - 返回删除的项数
  
- **`_enforce_capacity()`** (5分) - 容量限制
  - 超过容量时保留最新的N项
  - 基于 `timestamp` 排序，删除最旧的项
  
- **`query()`** (10分) - 查询和打分
  - 使用 **TF-IDF相似度** (权重0.5)
  - 加入 **时间衰减** (权重0.35，半衰期取 `max(300, ttl/2)` 秒)  
  - 加入 **重要性分数** (权重0.15)
  - 返回按综合得分排序的前top_k项

**实现提示：**
```python
# TF-IDF相似度：使用 self._tfidf_similarity() 和 self._doc_frequency()
# 时间衰减：使用 recency_score(now, mem.timestamp, half_life_seconds)
# 重要性：使用 normalize_importance(mem.importance)
```

---

#### 1.2 情节记忆（Episodic Memory）【15分】

文件：`src/memory/types/episodic_memory.py`

**要求填空的函数：**

- **`add()`** (8分) - 添加记忆
  - 将 `memory` 存入 `self._items[memory.id]`
  - 计算向量：`self._vectors[memory.id] = self.embed(memory.content)`
  - 持久化：`self._save()`
  
- **`query()`** (7分) - 查询和打分
  - 使用 **向量余弦相似度** (权重0.5)
  - 加入 **时间衰减** (权重0.3，半衰期7天)
  - 加入 **重要性分数** (权重0.2)
  - 返回前top_k项

**实现提示：**
```python
# 向量相似度：使用 cosine_similarity(query_vec, chunk_vec)
# 时间衰减：使用 recency_score(now, timestamp, half_life_seconds=7*24*3600)
```

---

#### 1.3 语义记忆（Semantic Memory）【15分】

文件：`src/memory/types/semantic_memory.py`

**要求填空的函数：**

- **`add()`** (8分) - 添加记忆
  - 流程同episodic_memory
  
- **`query()`** (7分) - 查询和打分
  - 使用 **向量相似度** + **词面匹配** 混合 (0.85\*向量 + 0.15\*词面，总体权重0.65)
  - 使用 **时间衰减** (权重0.1，半衰期30天)
  - 使用 **重要性分数** (权重0.25)
  - 综合得分：0.65\*rel + 0.25\*imp + 0.10\*rec
  - 返回前top_k项

**实现提示：**

```python
# 词面匹配：计算 query_terms 与 mem_terms 的交集比例
# 交集比例 = len(query_terms ∩ mem_terms) / max(1, len(query_terms))
```

---

#### 1.4 管理器（Memory Manager）【25分】

文件：`src/memory/manager.py`

**要求填空的函数：**

- **`add_memory()`** (5分)
  - 创建 `MemoryItem` 并调用 `module.add()`  
  - 标准化importance：`normalize_importance(importance)`
  
- **`update_memory()`** (5分)
  - 标准化importance（如果exists）
  - 调用 `module.update()`
  
- **`delete_memory()`** (5分)
  - 调用 `module.delete()`
  
- **`query_all()`** (5分)
  - 并行查询三类记忆，返回字典格式
  - key: `MemoryType.WORKING/EPISODIC/SEMANTIC`
  - value: `list[ScoredMemory]`
  
- **`forget_low_importance()`** (5分)
  - 遍历 episodic 和 semantic (不包括 working)
  - 删除所有 `importance < threshold` 的项
  - 返回删除总数

---

### Part 2：RAG系统实现 （25分）

文件：`src/rag/manager.py`

**要求填空的函数：**

- **`_split_text()`** (8分) - 文本分块
  - 按段优先：以 `\n\n` 分割文本
  - 折叠小段：相邻段若总长≤chunk_size，合并
  - 硬切分：超长段落按chunk_size切割
  - 返回所有块列表
  
- **`_retrieve_once()`** (8分) - 混合检索
  - 向量检索 + 词面匹配混合：score = 0.8*dense + 0.2*sparse
  - dense_score：向量余弦相似度
  - sparse_overlap：词面匹配比例
  - 返回按score排序的前top_k结果
  
- **`_merge_deduplicate()`** (9分) - 去重
  - 按 `chunk_id` 去重，保留最高分
  - 合并来自多个查询的结果列表
  - 返回去重后的结果

## 三、项目结构

```
code/
├── src/
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── models.py           # 数据模型（无需修改）
│   │   ├── manager.py          # 统一管理器 ← 需要填空
│   │   └── types/
│   │       ├── __init__.py
│   │       ├── episodic_memory.py    # 情节记忆 ← 需要填空
│   │       ├── semantic_memory.py    # 语义记忆 ← 需要填空
│   │       └── working_memory.py     # 工作记忆 ← 需要填空
│   ├── rag/
│   │   ├── __init__.py
|   |   ├── models.py			# 数据模型（无需修改）
│   │   └── manager.py          # RAG管理器 ← 需要填空
│   └── utils/
│       ├── __init__.py
│       └── memory_utils.py      # 工具函数（无需修改）
├── tests/
│   ├── __init__.py
│   └── test_grading.py         # 自动评测脚本
└── README.md                   # 本文件
```

## 四、使用方法

### 1. 编写代码

将TODO位置的代码补全。每个TODO都包含详细的实现说明。

### 2. 本地测试

```bash
# 进入code目录
cd code

# 运行自动评测
python tests/test_grading.py

# 或使用pytest
python -m pytest tests/test_grading.py -v
```

### 3. 理解数据结构

所有必需的数据结构定义在 `src/memory/models.py` 和`src/rag/models.py`中：

- `MemoryItem`：单条记忆（包含id、content、timestamp、importance等）
- `ScoredMemory`：带打分的记忆结果（包含score、relevance_score、recency_score等）
- `RetrievalResult`：RAG检索结果

### 4. 使用工具函数

在 `src/utils/memory_utils.py` 中已提供的工具函数：
- `cosine_similarity(vec1, vec2)`：向量余弦相似度
- `tf_vector(text)`：TF向量化
- `normalize_importance(score)`：标准化重要性到[0,1]
- `recency_score(now, timestamp, half_life_seconds)`：时间衰减得分
- `tags_match(mem_tags, filter_tags)`：标签匹配
- `tokenize(text)`：分词
- 等等

## 五、评分标准

### 自动评测

运行 `python tests/test_grading.py` 后，将输出详细的测试报告：

```
============================================================
自动评测报告
============================================================

Working Memory:
  [PASS] working_memory_cleanup: 5/5
  [PASS] working_memory_capacity: 5/5
  [PASS] working_memory_query: 10/10
  小计: 20/20

Episodic Memory:
  [PASS] episodic_memory_add: 8/8
  [PASS] episodic_memory_query: 7/7
  小计: 15/15

...

总分: 100/100 (100.0%)
============================================================
```

### 评分规则

- **PASS**：完全通过测试
- **PARTIAL**：部分通过，获得一半分数
- **FAIL**：未通过或返回错误结果
- **ERROR**：代码异常导致无法运行

## 六、重要提示

1. **框架代码**：类定义、`__init__`、`save()`、`load()` 等已提供，无需修改
2. **返回类型**：严格按照函数签名的返回类型返回，不要返回 `None`
3. **打分权重**：严格按照要求的权重进行加权融合，不要随意修改
4. **边界情况**：处理空列表、没有候选项等边界情况，避免异常
5. **持久化**：episodic 和 semantic memory 需要将数据保存到JSON文件

## 七、拓展提高

有兴趣的同学可以继续尝试以下内容：

- 接入一个真实`embedding`模型，然后尝试一下看看结果
- 尝试实现HyDE和MQE，看看高级检索策略对RAG的影响
- 使用一个成熟的向量数据库来替换自己实现的向量数据库，相比之下，成熟的向量数据库有什么优点？
