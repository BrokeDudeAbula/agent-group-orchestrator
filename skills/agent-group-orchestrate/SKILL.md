---
name: agent-group-orchestrate
description: Use when Codex should run or design a project-local multi-agent workflow with auto-orchestration, worker selection, task DAGs, risk gates, task ledgers, and current-state memory updates.
---

# Agent Group Orchestrate

Use this skill for project-local multi-agent coordination. The target instance is usually `.codex/agent_group/`, but accept an explicit path from the user.

## Workflow

1. Locate the agent group instance. If missing, suggest or run `scripts/init_agent_group.py` when the user wants initialization.
2. Read `rules/BOOTSTRAP.md` and `current/STATE.md` first.
3. Read `rules/SUB_AGENT_EXECUTION.md`, `rules/WORKER_REGISTRY.md`, and `rules/ROUTING_POLICY.md` when worker selection or DAG construction is needed.
4. Classify risk using `references/risk-policy.md`.
5. Build a small task DAG and choose workers. Skip irrelevant workers explicitly.
6. For R3/R4 work, ask for confirmation before edits or long/remote commands.
7. Dispatch each selected non-main worker through the configured sub-agent backend. The main orchestrator supervises only; it must not directly perform worker-scoped development, testing, benchmarking, repository research, architecture, or review work.
8. Write worker outputs to `current/agent_outputs/`.
9. Update `current/tasks.csv`, `current/STATE.md`, and durable ledgers according to `references/memory-sync-sop.md`.
10. End with a compact report: goal status, workers used, sub-agent references, files written, evidence spot checks, blockers, next step.

## Reference Loading

- Read `references/routing-policy.md` for DAG patterns.
- Read `references/worker-registry.md` when creating or revising worker definitions.
- Read `references/sub-agent-execution.md` for backend-neutral sub-agent dispatch requirements.
- Read `references/memory-sync-sop.md` before memory updates.
- Read `references/output-contract.md` before writing worker outputs.

## Guardrails

- Do not treat plugin examples as live project state.
- Do not run remote, destructive, or long profiling tasks without an explicit gate.
- Do not perform non-main worker work directly; dispatch it to Codex or Claude Code CLI sub-agents.
- Preserve user changes in dirty worktrees.
- Prefer structured updates over free-form state drift.
