# Chapter 5 Homework: LangGraph Workflow

本作业对应第五章中新增的 LangGraph 内容，重点不是继续补 Prompt 或 Tool 的基础概念，而是练习：

> 如何把一个多步任务组织成一张真正可执行的图。

## 目标

补全 `langgraph_homework_template.py` 中的 TODO，让图流程完成下面这条主链路：

```text
1. 判断任务是否需要读取 Markdown 文件
2. 如果需要，就调用工具读取文件
3. 从 Markdown 中提取核心信息
4. 把结果整理成最终答复
```

## 运行方式

```bash
cd minimal_agents
python hw/chapter-5/langgraph/langgraph_homework_template.py
```

## 你需要补全的内容

主要 TODO 有 5 个：

1. 设计路由节点的输出
2. 编写路由函数，决定走哪条边
3. 在读取节点中调用 `ToolRegistry`
4. 在总结节点中整理 Markdown 内容
5. 把节点和边串成完整 `StateGraph`

## 作业重点

完成这份作业时，建议重点思考：

1. 哪些信息应该进入 State；
2. 哪些步骤应该拆成单独 Node；
3. 条件分支应该放在什么位置；
4. 为什么图结构比一段很长的 `if/else + while` 更容易维护。
