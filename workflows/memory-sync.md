# Agent Group Memory Sync

Use this workflow for maintaining agent group memory after work completes or before a context handoff.

`<skill-root>` is the directory that contains `SKILL.md`. Script paths below are relative to that directory. Instance files are inside the target project.

## Policy source

Use instance `rules/MEMORY_SYNC_SOP.md`. Do not open the skill-pack copy of the same procedure.

## Working set

Read `current/STATE.md`, `current/tasks.csv`, and `memory/PROJECT_FACTS.md`. Open `rules/MEMORY_SYNC_SOP.md` when you will write or compact. Open `memory/LEDGER_INDEX.md` before a ledger, then read that ledger's `## Summary` and `## Recent` only.

## Workflow

1. Locate the target instance using an explicit path, an existing `.agent_group/`, `.claude/agent_group/`, or `.codex/agent_group/`, or the host default from `workflows/init.md`.
2. Update `current/STATE.md` and `current/tasks.csv` first.
3. Update `memory/PROJECT_FACTS.md` when a stable fact changed. Keep that file compact.
4. Append a short ledger entry for a task change, a decision, a risk, or a milestone. Do not rewrite old decisions. Do not delete risks; mark them `mitigated`, `closed`, or `accepted`.
5. Keep raw worker evidence in `current/agent_outputs/` until phase close.
6. When the phase is done, archive `current/` and roll durable ledgers:

```bash
python3 <skill-root>/scripts/compact_memory.py --target <agent-group-path> --archive-name <yyyymmdd_topic> --dry-run
```

7. Review the dry run, then run without `--dry-run` to apply it.
8. Expect the helper to recreate concise `current/STATE.md`, `current/epic.md`, `current/acceptance.md`, and `current/tasks.csv` unless `--no-reset-current` is used. Ledger overflow goes to `archive/ledgers/`.
9. Validate:

```bash
python3 <skill-root>/scripts/validate_agent_group.py --strict <agent-group-path>
```

If validation names a missing heading, fix that heading. Do not open a schema document first.

## Hot memory

- `current/STATE.md`: active state only.
- `current/tasks.csv`: active epic tasks only. `depends_on` records DAG edges.
- `memory/PROJECT_FACTS.md`: stable facts, read on an orchestrate turn.
- `memory/LEDGER_INDEX.md`: the door to durable ledgers. It is not a second copy of them.

## Guardrails

- Never delete evidence without archiving it.
- Do not archive `rules/`, `agents/`, or the durable ledger files themselves. Roll their overflow instead.
- Keep `current/STATE.md` concise.
