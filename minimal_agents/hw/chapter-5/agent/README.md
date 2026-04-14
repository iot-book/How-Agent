# Chapter 5 Homework: Custom Agent Loop

本作业练习 `05_智能体` 的核心概念：**Agent loop 可以被开发者定制**。

前面的 chapter-3 已经练习过 Tool 和 Skill，所以这个作业不会重点考察工具实现或 Skill 注入。这里的重点是设计并补全一个新的 `ChecklistAgent` 控制循环。

## 目标

补全 `checklist_agent_homework_template.py` 中的 TODO，让 Agent 完成下面的流程：

```text
1. 生成 checklist
2. 逐项执行 checklist item
3. 检查每一步结果
4. 如果检查失败，带 feedback 重试一次
5. 汇总所有步骤，输出最终答案
```

这个 Agent 不同于示例里的 ReActAgent：

```text
ReActAgent:
模型通过 Thought / Action / Observation / Finish 主导循环。

ChecklistAgent:
程序先固定 loop 结构，模型负责生成 checklist、执行步骤、检查结果和汇总。
```

## 运行方式

```bash
python hw/chapter-5/agent/checklist_agent_homework_template.py
```

默认使用 `ScriptedLLMBackend`，不需要外部 LLM API，也不需要 API key。

## 你需要补全的内容

主要 TODO 有 6 个：

1. 创建 checklist
2. 格式化历史步骤结果
3. 执行单个 checklist item
4. 检查单步结果
5. 汇总最终答案
6. 串起完整 Agent loop

工具函数、工具注册和 JSON 解析 helper 已经提供好。请把注意力放在 Agent loop 本身。
