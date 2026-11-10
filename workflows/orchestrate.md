# Agent Group Orchestrate

Use this workflow for project-local multi-agent coordination. Resolve the instance path with the same rules as `workflows/init.md`: explicit path, one existing standard instance (`.agent_group/`, `.claude/agent_group/`, or `.codex/agent_group/`), otherwise the host default. Ask the user when more than one standard instance exists and no path was chosen.

`<skill-root>` is the directory that contains `SKILL.md`. Reference paths below are relative to that directory. `rules/`, `current/`, and `memory/` paths are inside the target instance.

## Workflow

1. Locate the agent group instance. If missing, suggest or run `python3 <skill-root>/scripts/init_agent_group.py` when the user wants initialization.
2. Read `rules/BOOTSTRAP.md` and `current/STATE.md` first.
3. Read `rules/SUB_AGENT_EXECUTION.md`, `rules/WORKER_REGISTRY.md`, and `rules/ROUTING_POLICY.md` when worker selection or DAG construction is needed.
4. Classify risk using `<skill-root>/references/risk-policy.md`.
5. Build a small task DAG and choose workers. Skip irrelevant workers explicitly.
6. For R3/R4 work, ask for confirmation before edits or long/remote commands.
7. Dispatch each selected non-main worker through the configured sub-agent backend. The main orchestrator supervises only; it must not directly perform worker-scoped development, testing, benchmarking, repository research, architecture, or review work.
8. Write worker outputs to `current/agent_outputs/`.
9. Update `current/tasks.csv`, `current/STATE.md`, and durable ledgers according to `<skill-root>/references/memory-sync-sop.md`.
10. End with a compact report: goal status, workers used, sub-agent references, files written, evidence spot checks, blockers, next step.

## Reference Loading

- Read `<skill-root>/references/routing-policy.md` for DAG patterns.
- Read `<skill-root>/references/worker-registry.md` when creating or revising worker definitions.
- Read `<skill-root>/references/sub-agent-execution.md` for host-neutral sub-agent dispatch requirements.
- Read `<skill-root>/references/memory-sync-sop.md` before memory updates.
- Read `<skill-root>/references/output-contract.md` before writing worker outputs.

## Guardrails

- Do not treat `<skill-root>/examples/` as live project state.
- Do not run remote, destructive, or long profiling tasks without an explicit gate.
- Do not perform non-main worker work directly; dispatch it to a compatible sub-agent backend.
- Preserve user changes in dirty worktrees.
- Prefer structured updates over free-form state drift.
