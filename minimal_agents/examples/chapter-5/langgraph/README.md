# 第五章 LangGraph 示例代码

本目录对应第五章中新增的 LangGraph 小节，目标是帮助读者把“State、Node、Edge”这些概念真正落到代码里。

## 目录说明

- `teaching_langgraph_demo.py`：最小可运行的 LangGraph 示例。这个示例会把读取 Markdown 文件、整理摘要、输出最终结果组织成一张图，并且复用 `minimal_agents` 里的 `ToolRegistry`。
- `sample_student_task.md`：示例中要读取的 Markdown 文件。

## 运行方式

先在仓库根目录安装依赖：

```bash
pip install -r minimal_agents/requirements.txt
```

然后进入 `minimal_agents` 目录运行：

```bash
cd minimal_agents
python examples/chapter-5/langgraph/teaching_langgraph_demo.py
```

## 学习重点

运行这个示例时，建议重点观察三件事：

1. State 中放了哪些字段；
2. 每个 Node 分别在读写哪些状态；
3. Edge 是怎样决定流程走向的。

这一示例不依赖在线模型，因此更适合先把 LangGraph 的基础结构看懂，再继续扩展更复杂的 Agent 流程。
