# Agent Lesson Note

Agent is the controller that organizes an LLM, context, tools, and a control loop.

Tool is an executable capability. It performs a concrete action, such as reading a
file, searching data, or calculating a value.

Skill is a reusable task method. It gives the model workflow guidance, constraints,
and output expectations.

A useful agent loop usually includes several decisions:

- what context to send to the model
- which tool or sub-agent should handle the next step
- how to record observations
- when to retry
- when to stop and summarize
