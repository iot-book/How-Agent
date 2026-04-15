## Quick start

From repository root:

```bash
pip install -e ./minimal_agents[test]
```

Or install the teaching dependencies directly:

```bash
pip install -r minimal_agents/requirements.txt
```

Run subproject tests:

```bash
pytest -c minimal_agents/pyproject.toml minimal_agents/tests
```

Run local examples from the subproject directory:

```bash
cd minimal_agents
python examples/hello_minimal.py
python examples/chapter-2/prompt/teaching_prompt_demo.py
python examples/chapter-3/tool/teaching_tools_demo.py
python examples/chapter-3/skill/teaching_skills_demo.py
python examples/chapter-4/mcp/teaching_mcp_demo.py
python examples/chapter-5/agent/teaching_minimal_demo.py
python examples/chapter-5/agent/teaching_react_demo.py
python examples/chapter-5/agent/teaching_plan_execute_demo.py
python examples/chapter-5/agent/teaching_full_capabilities_demo.py
python examples/chapter-5/langgraph/teaching_langgraph_demo.py
python examples/chapter-7/gateway/teaching_gateway_demo.py
```

Teaching examples and homework are grouped by chapter:

```text
examples/chapter-x/<topic>/
hw/chapter-x/<topic>/
```

You can browse `examples/tutorial_examples.md` for a chapter-by-chapter index.

## GLM 4.7 smoke check

Set your API key in the environment (do not hardcode secrets):

```bash
export GLM_API_KEY=your_key_here
```

Run the online smoke script:

```bash
cd minimal_agents && python examples/glm47_smoke.py
```
