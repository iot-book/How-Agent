# 教程配套代码示例

本目录中的教学示例与教程章节一一对应，便于将文中的代码片段直接落实到 `minimal_agents` 这一最小智能体实现中。

## 章节与示例对应关系

- 第二章 Prompt：`chapter-2/prompt/teaching_prompt_demo.py`
  说明如何通过 `system_prompt` 将提示词注入 `MinimalAgent` 的消息构造过程。
- 第三章 Tools：`chapter-3/tool/teaching_tools_demo.py`
  说明如何通过 `ToolRegistry.register_function(...)` 注册本地工具，并让 `MinimalAgent` 在推理循环中调用该工具。
  配套工具文件：`chapter-3/tool/teaching_weather_tool.py`
- 第三章 Skills：`chapter-3/skill/teaching_skills_demo.py`
  说明如何使用 `SkillLoader`、`SkillResolver` 和 `SKILL.md` 将任务方法注入智能体。
  配套 Skill 目录：`chapter-3/skill/skills_demo/markdown_reader/`
- 第四章 MCP：`chapter-4/mcp/teaching_mcp_demo.py`
  说明如何通过 `StdioMCPClient` 与 `register_mcp_tools(...)` 将本地 MCP Server 暴露的工具桥接到 `ToolRegistry` 中。
- 第四章 MCP 本地 stdio Server：`chapter-4/mcp/teaching_stdio_weather_server.py`
  说明如何使用官方 `mcp` Python SDK 启动一个最小本地 MCP Server，供宿主应用以 `stdio` 方式接入。
  配套业务函数：`chapter-4/mcp/teaching_weather_tools.py`
- 第五章 Agent 最小闭环：`chapter-5/agent/teaching_minimal_demo.py`
  说明 `MinimalAgent` 如何接收输入并返回模型结果。
- 第五章 ReAct Agent：`chapter-5/agent/teaching_react_demo.py`
  说明 `ReActAgent` 如何使用内置 `Thought` / `Finish` 动作组织推理过程。
- 第五章 Plan-and-Execute Agent：`chapter-5/agent/teaching_plan_execute_demo.py`
  说明 `PlanAndExecuteAgent` 如何先规划、再执行、最后汇总。
- 第五章 Agent 综合能力：`chapter-5/agent/teaching_full_capabilities_demo.py`
  说明如何把本地 Tool、MCP Tool 和 Skill 组合进同一个 `MinimalAgent`。
  配套 Skill 目录：`chapter-5/agent/skills_demo/`
- 第五章 LangGraph：`chapter-5/langgraph/teaching_langgraph_demo.py`
  说明如何用 `StateGraph` 把“路由、读取文件、整理摘要、输出答案”组织成一张可执行的图。
  配套文件：`chapter-5/langgraph/sample_student_task.md`
- 第六章 移动端智能体：`chapter-6/mobile/`
  提供一个 Android 端最小移动智能体示例，展示 PDA 循环在移动端场景中的基本实现方式。
  配套说明文件：`chapter-6/mobile/README.md`
- 第八章 记忆与检索：`chapter-8/memory/`
  提供一个最小记忆系统与 RAG 检索原型，帮助读者理解记忆模块、检索模块与统一管理器之间的关系。
  配套说明文件：`chapter-8/memory/README.md`
- 第九章 Dify 工作流：`chapter-9/dify/`
  提供本章中用到的 Dify 工作流导出文件，便于直接导入平台查看与复用。
  配套说明文件：`chapter-9/dify/README.md`
- 第七章 Gateway：`chapter-7/gateway/teaching_gateway_demo.py`
  说明如何在 `MinimalAgent` 前增加一层最小 Gateway，完成“请求接入、消息归一化、路由到 Agent、结果回传”这一条主链路。
  配套文件：`chapter-7/gateway/teaching_gateway_tools.py`、`chapter-7/gateway/gateway_sample_note.md`

## 建议的教程使用方式

如果教程中的代码示例需要与本仓库保持一致，可以优先引用以下接口：

- Prompt 章节引用 `MinimalAgent(..., system_prompt=...)`
- Tools 章节引用 `ToolRegistry.register_function(...)`
- Skills 章节引用 `SkillLoader` 与 `SkillResolver`
- MCP 章节引用 `register_mcp_tools(...)`

这样可以保证读者看到的示例，不只是独立代码片段，而是能够嵌入同一个最小 Agent 实现中的真实用法。
