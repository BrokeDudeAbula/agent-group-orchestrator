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

This file is the runtime entry. Read it with `current/STATE.md`. Do not open a skill-pack reference for the same rules.

## Working set

For an orchestrate turn, also read:

- `current/tasks.csv`
- `memory/PROJECT_FACTS.md`

That is the hot set. `memory/PROJECT_FACTS.md` is compact; read it whole. Do not open another file unless a trigger below matches.

## On-demand index

Open one row, and only when its trigger is true. Then stop.

| File | Open only when |
| --- | --- |
| `rules/ROUTING_POLICY.md` | Adding a worker beyond `repo-explorer` and `kernel-dev` |
| `rules/WORKER_REGISTRY.md` | A role other than those two is under consideration |
| `rules/SUB_AGENT_EXECUTION.md` | Dispatching a sub-agent |
| `rules/MEMORY_SYNC_SOP.md` | Writing durable memory or closing a phase |
| `rules/RUNBOOK_REMOTE.md` | An R4 remote or long command is proposed |
| `memory/LEDGER_INDEX.md` | History from an earlier task or phase is required |
| `current/epic.md` | Scope is unclear |
| `current/acceptance.md` | Checking whether the goal is done |

`memory/LEDGER_INDEX.md` is the only door to durable ledgers. From there, read `## Summary` and `## Recent` of the one ledger you need. Do not load a ledger in full.

## Default mode

Use `auto-orchestrate` when the user provides a goal and does not name workers.

1. Classify risk with the summary below.
2. Do cheap read-only R0/R1 lookups in this session. Dispatch a sub-agent only for substantial work.
3. Default DAG: `repo-explorer`, then `kernel-dev` if a change is required. A read-only goal stops after `repo-explorer`. Record why any other worker is added.
4. Pass each sub-agent a short upstream summary and file paths.
5. Keep each worker output within 120 lines and 6000 characters.
6. Update `current/STATE.md`, `current/tasks.csv`, and `memory/PROJECT_FACTS.md` when a fact changed.
7. At phase end, run `compact_memory.py` so `current/` is archived and ledgers roll forward.

## Risk summary

- R0: read-only. Proceed.
- R1: agent-group metadata and documentation. Proceed, and report files changed.
- R2: non-core docs, scripts, or reports. Proceed when the scope is explicit.
- R3: core source, build, deployment, database, or production behavior. Ask first.
- R4: remote, long, destructive, profiling, or cost-incurring work. Ask first.
