# 第五章示例代码

本目录对应第五章“智能体”的配套示例，重点展示一个最小 Agent 如何逐步扩展出更完整的执行能力。

## 目录说明

- `teaching_minimal_demo.py`：最小 `MinimalAgent` 示例，只保留最基本的输入与输出流程。
- `teaching_react_demo.py`：演示 ReAct 风格的思考与行动循环。
- `teaching_plan_execute_demo.py`：演示先规划、再执行、最后汇总的工作流。
- `teaching_full_capabilities_demo.py`：把 Tool、Skill 与 MCP 能力组合到同一个 Agent 中。
- `skills_demo/`：第五章示例中用到的 Skill 定义目录。

## 运行方式

先在仓库根目录安装依赖：

```bash
pip install -e ./minimal_agents[test]
```

然后进入 `minimal_agents` 目录运行示例：

```bash
cd minimal_agents
python examples/chapter-5/agent/teaching_minimal_demo.py
python examples/chapter-5/agent/teaching_react_demo.py
python examples/chapter-5/agent/teaching_plan_execute_demo.py
python examples/chapter-5/agent/teaching_full_capabilities_demo.py
```

如果需要统一跑测试，可以在仓库根目录执行：

```bash
pytest -c minimal_agents/pyproject.toml minimal_agents/tests
```
