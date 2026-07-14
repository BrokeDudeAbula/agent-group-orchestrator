# Routing Policy

Default mode is `auto-orchestrate`: when the user gives a goal, the main orchestrator chooses workers, builds a task DAG, dispatches selected non-main workers as sub-agents, gathers outputs, updates memory, and reports the result.

The main orchestrator is a supervisor only. It must not directly perform worker-scoped implementation, testing, benchmarking, repository discovery, upstream research, architecture analysis, or final review. See `references/sub-agent-execution.md`.

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

Each selected non-main worker must be executed by a compatible sub-agent backend. Codex and Claude Code CLI adapters may expose different launch primitives, but both must receive the same worker role file, task id, scope, risk boundary, expected output path, and output contract. If sub-agents are unavailable, the workflow is blocked rather than reassigned to the main orchestrator.

Task IDs should be stable and sortable:

```text
AUTO-<yyyymmdd>-<nn>
```

Worker outputs should go to:

```text
current/agent_outputs/<task_id>_<worker>.md
```

Worker outputs should record the execution backend and sub-agent reference when the backend provides one.

When tasks have ordering requirements, record dependencies in `current/tasks.csv` using a `depends_on` column. Use stable task ids and separate multiple dependencies with semicolons.
