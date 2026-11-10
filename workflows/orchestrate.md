# Agent Group Orchestrate

Use this workflow for project-local multi-agent coordination. Resolve the instance with the same rules as `workflows/init.md`: explicit path, one existing standard instance (`.agent_group/`, `.claude/agent_group/`, or `.codex/agent_group/`), otherwise the host default. Ask the user when more than one standard instance exists and no path was chosen.

`<skill-root>` is the directory that contains `SKILL.md`. `rules/`, `current/`, and `memory/` paths are inside the target instance.

## Policy source

Instance `rules/` is the only runtime policy. Do not open skill-pack references for the same topic.

## Working set

Read these and stop:

1. `rules/BOOTSTRAP.md`
2. `current/STATE.md`
3. `current/tasks.csv`
4. `memory/PROJECT_FACTS.md`

`memory/PROJECT_FACTS.md` stays compact. Read it whole. Open another file only when a BOOTSTRAP trigger matches the current step. History goes through `memory/LEDGER_INDEX.md`, then the summary and recent tail of the one ledger that index names. Do not load a ledger in full.

## Workflow

1. Locate the instance. If it is missing, suggest or run `python3 <skill-root>/scripts/init_agent_group.py` when the user wants initialization.
2. Read the working set above.
3. Do cheap read-only R0/R1 work in this session: a few named-file lookups, or a narrow question. Do not spawn a sub-agent for that. Agent-group metadata edits stay here too.
4. Default DAG is `repo-explorer`, then `kernel-dev` when a change is required. A read-only goal stops after `repo-explorer`. Add `reviewer`, `perf-analyst`, `oss-scout`, `architect`, or `runner` only for a reason recorded in the task notes. Open `rules/ROUTING_POLICY.md` and `rules/WORKER_REGISTRY.md` only when adding a worker beyond that default.
5. Classify risk from the BOOTSTRAP summary. R3/R4 wait for confirmation.
6. Dispatch each substantial non-main task as one sub-agent. Open `rules/SUB_AGENT_EXECUTION.md` at the first dispatch of the turn. The prompt carries the role-file path, a short upstream summary, and file paths. Do not paste upstream outputs.
7. Write worker outputs under `current/agent_outputs/`. Keep each output within 120 lines and 6000 characters. Link evidence instead of pasting logs.
8. Update `current/STATE.md` and `current/tasks.csv`. Update `memory/PROJECT_FACTS.md` when a stable fact changed. Append a ledger line without rereading the ledger; use the index when prior context is required.
9. When every active task is `done` or `dropped`, or the user closes the phase, archive hot state and roll ledgers:

```bash
python3 <skill-root>/scripts/compact_memory.py --target <agent-group-path> --archive-name <yyyymmdd_topic> --dry-run
```

Apply the same command without `--dry-run` when the dry run only archives `current/` and rolls ledgers.

10. Report goal status, workers used, workers skipped and why, sub-agent references, files written, blockers, and the next step.

## Guardrails

- Do not treat `<skill-root>/examples/` as live project state.
- Do not run remote, destructive, or long tasks without an explicit gate.
- Preserve user changes in dirty worktrees.
- Keep `current/STATE.md` short enough to re-read next turn.
