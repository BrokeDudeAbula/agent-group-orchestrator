---
ag_schema: v1
doc_id: AG-RULE-BOOTSTRAP
category: rules
doc_type: bootstrap
authority: canonical
lifecycle: hot
read_policy: always
write_policy: controlled_update
risk_level: R1
owner: main-orchestrator
---

# Bootstrap

At the start of an agent-group workflow, read:

```text
rules/BOOTSTRAP.md
rules/SUB_AGENT_EXECUTION.md
current/STATE.md
```

Then read on demand:

```text
rules/WORKER_REGISTRY.md
rules/ROUTING_POLICY.md
rules/MEMORY_SYNC_SOP.md
memory/PROJECT_FACTS.md
memory/TASK_LEDGER.md
memory/PROGRESS_LEDGER.md
memory/DECISIONS.md
memory/RISKS.md
memory/ROADMAP.md
current/epic.md
current/acceptance.md
current/prompt.md
current/tasks.csv
```

## Default Mode

Use `auto-orchestrate` when the user provides a goal without assigning workers.

The main orchestrator should:

1. Clarify the goal only when necessary.
2. Classify risk.
3. Select workers from `WORKER_REGISTRY.md`.
4. Build a small DAG from `ROUTING_POLICY.md`.
5. Apply R3/R4 gates before sensitive work.
6. Dispatch selected non-main workers through the configured sub-agent backend.
7. Monitor sub-agent progress and blockers without doing worker-scoped work directly.
8. Store worker outputs in `current/agent_outputs/`.
9. Spot-check evidence, synchronize memory using `MEMORY_SYNC_SOP.md`, and report status, sub-agent references, files changed, blockers, and next step.

The main orchestrator is a supervisor only. It must not directly perform development, testing, benchmarking, repository discovery, upstream research, architecture analysis, or final review assigned to workers.

## Risk Gate Summary

- R0: read-only.
- R1: agent-group metadata and documentation.
- R2: non-core project docs, scripts, or reports.
- R3: core source, build, deployment, database, or production behavior.
- R4: remote, long-running, destructive, profiling, or cost-incurring work.

R3 and R4 require explicit user confirmation.
