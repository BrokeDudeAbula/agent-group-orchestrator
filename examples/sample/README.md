# Sample Agent Group Instance

This sample shows a neutral project-local agent group instance. It includes:

- hot state in `current/`
- durable memory in `memory/`
- worker evidence in `current/agent_outputs/`
- generic workers and rules

The sample scenario is an API latency audit. It intentionally avoids domain-specific project names, hardware names, private paths, or vendor-specific assumptions.

The default DAG is `repo-explorer` then `kernel-dev`. This fixture adds `perf-analyst` because the goal is a latency claim, and `reviewer` because the next change would be R3. Those reasons are in `current/tasks.csv` notes.

This tree is a skill-pack fixture, not a live workspace. Initialize a live instance in the target project at `.agent_group/`, `.claude/agent_group/`, or `.codex/agent_group/`.
