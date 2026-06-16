# Routing Policy

Default mode is `auto-orchestrate`: when the user gives a goal, the main orchestrator chooses workers, builds a task DAG, gathers outputs, updates memory, and reports the result.

Common DAGs:

```text
Read-only analysis:
repo-explorer -> perf-analyst? -> oss-scout? -> architect? -> reviewer -> main-orchestrator

Documentation or metadata:
repo-explorer -> main-orchestrator or kernel-dev -> reviewer -> main-orchestrator

Core implementation:
repo-explorer -> perf-analyst? -> oss-scout? -> architect -> user gate -> kernel-dev -> reviewer -> validation gate -> runner -> reviewer -> main-orchestrator

Remote or long validation:
repo-explorer -> perf-analyst? -> user gate -> runner -> perf-analyst -> reviewer -> main-orchestrator
```

Worker selection should be driven by `rules/WORKER_REGISTRY.md` in the target instance. Skip workers when their contribution is not relevant, but record the reason in the orchestrator output.

Task IDs should be stable and sortable:

```text
AUTO-<yyyymmdd>-<nn>
```

Worker outputs should go to:

```text
current/agent_outputs/<task_id>_<worker>.md
```
