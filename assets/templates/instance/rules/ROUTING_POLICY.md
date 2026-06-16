---
ag_schema: v1
doc_id: AG-RULE-ROUTING-POLICY
category: rules
doc_type: routing_policy
authority: canonical
lifecycle: warm
read_policy: on_demand
write_policy: controlled_update
risk_level: R1
owner: main-orchestrator
---

# Routing Policy

Default mode is `auto-orchestrate`. When the user gives a goal, the main orchestrator chooses workers, splits tasks, applies risk gates, collects outputs, updates memory, and reports the result.

## Worker Selection

Read `rules/WORKER_REGISTRY.md` before selecting workers. Use this file for DAG patterns and risk gates.

## Default DAGs

### Read-only analysis

```text
repo-explorer
  -> perf-analyst?       # include only for performance or measurement claims
  -> oss-scout?          # include for planning, upstream comparison, or ecosystem research
  -> architect?          # include when a design decision or implementation plan is needed
  -> reviewer
  -> main-orchestrator
```

### Documentation or metadata task

```text
repo-explorer
  -> main-orchestrator or kernel-dev
  -> reviewer
  -> main-orchestrator
```

### Core implementation task

```text
repo-explorer
  -> perf-analyst?
  -> oss-scout?
  -> architect
  -> user confirms write scope
  -> kernel-dev
  -> reviewer
  -> validation gate
  -> runner?
  -> reviewer
  -> main-orchestrator
```

### Long, remote, or expensive validation

```text
repo-explorer
  -> perf-analyst?
  -> user confirms command, target, duration, output path, and stop condition
  -> runner
  -> perf-analyst?
  -> reviewer
  -> main-orchestrator
```

## Risk Levels

- R0: read-only inspection.
- R1: agent-group metadata or documentation writes.
- R2: non-core project docs, scripts, or reports.
- R3: core source, build, deployment, database, CUDA, or production behavior changes.
- R4: remote machines, long jobs, profiling, destructive operations, or cost-incurring actions.

R3 and R4 require an explicit user gate before execution.

## Task Naming

Use stable task ids:

```text
AUTO-<yyyymmdd>-<nn>
```

## Worker Outputs

Default path:

```text
current/agent_outputs/<task_id>_<worker>.md
```

Each worker output must include scope, inputs read, commands run, conclusion, artifacts, risks or blockers, and recommended next step.

