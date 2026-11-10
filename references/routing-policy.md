# Routing Policy

Runtime copy: the instance file `rules/ROUTING_POLICY.md`.
Load this reference only when that file does not exist. Do not load both.

Default mode is `auto-orchestrate`. The main orchestrator chooses a small DAG, dispatches substantial non-main work, updates the hot memory files, and reports the result.

## Default DAG

```text
repo-explorer -> kernel-dev
```

A read-only goal stops after `repo-explorer`. The main orchestrator writes the user report.

Add another worker only for a reason recorded in `current/tasks.csv` notes:

| Worker | Add only when |
| --- | --- |
| `perf-analyst` | The goal is a measurement or performance claim |
| `oss-scout` | The goal needs upstream or ecosystem comparison |
| `architect` | Several designs must be compared before editing |
| `reviewer` | The user asked for review, evidence is disputed, or the next step is R3/R4 |
| `runner` | A gated build, test, or remote validation is required |

## Inline work

Cheap read-only R0/R1 lookups stay in the main session. Do not spawn a sub-agent to read a few named files. Broad discovery, implementation, benchmarks, upstream research, design comparison, and formal review are still worker tasks.

## Dispatch

Each substantial non-main task is one sub-agent. The prompt gets the role-file path, a short upstream summary, and file paths. It does not include full upstream outputs. If no sub-agent backend is available, mark the workflow blocked.

Task ids:

```text
AUTO-<yyyymmdd>-<nn>
```

Worker outputs:

```text
current/agent_outputs/<task_id>_<worker>.md
```

Keep each output within 120 lines and 6000 characters. Record dependencies in `current/tasks.csv` with `depends_on`, separated by semicolons.
