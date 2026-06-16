---
name: agent-group-memory-sync
description: Use when Codex should update, compact, archive, or validate an agent group current state, task ledger, progress ledger, decisions, risks, and worker outputs.
---

# Agent Group Memory Sync

Use this skill for maintaining agent group memory after work completes or before a context handoff.

## Workflow

1. Locate the target agent group instance, usually `.codex/agent_group/`.
2. Read `references/directory-contract.md` and confirm the target has the required memory shape.
3. Read `references/memory-sync-sop.md`.
4. Read `references/memory-schema.md` when creating files, changing file structure, repairing memory, or doing strict validation.
5. Read `current/STATE.md`, `current/tasks.csv`, and recent `current/agent_outputs/`.
6. Update hot state first, durable ledgers second.
7. If cleaning a completed phase, run:

```bash
python3 scripts/compact_memory.py --target <agent-group-path> --archive-name <yyyymmdd_topic> --dry-run
```

8. Review the dry run, then run without `--dry-run` only when the user wants the archive applied.
9. Validate the instance afterward:

```bash
python3 scripts/validate_agent_group.py --strict <agent-group-path>
```

## Memory Shape Contract

Required hot memory:

- `current/STATE.md`: concise active state only.
- `current/tasks.csv`: active epic tasks only.
- `current/agent_outputs/`: raw worker evidence for the current phase.

Required durable memory:

- `memory/TASK_LEDGER.md`: durable task records.
- `memory/PROGRESS_LEDGER.md`: append-only progress summaries.
- `memory/DECISIONS.md`: append-only decisions; supersede instead of deleting.
- `memory/RISKS.md`: risk records; close, mitigate, or accept instead of deleting.
- `memory/PROJECT_FACTS.md`: stable facts, paths, entrypoints, dependencies, and environment notes.

## Write Rules

- Update `current/STATE.md` before durable ledgers.
- Keep `current/STATE.md` short; link worker outputs instead of copying long logs.
- Do not mix multiple epics in `current/tasks.csv`.
- Do not put raw benchmark logs or command dumps into durable ledgers; summarize and link artifacts.
- Do not delete worker outputs during sync.
- Do not rewrite historical decisions or progress except to fix a clear typo.
- Do not remove risks; update status to `mitigated`, `closed`, or `accepted`.
- Archive old `current/` before resetting a phase.

## Guardrails

- Never delete evidence without archiving it.
- Do not remove decisions or risks; supersede or close them.
- Keep `current/STATE.md` concise.
