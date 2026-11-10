---
ag_schema: v1
doc_id: AG-RULE-MEMORY-SYNC-SOP
category: rules
doc_type: memory_sync_sop
authority: canonical
lifecycle: warm
read_policy: on_demand
write_policy: controlled_update
risk_level: R1
owner: main-orchestrator
---

# Memory Sync SOP

This file is the runtime memory procedure. Do not also read the skill-pack memory references. Open it when writing durable memory or closing a phase.

## Hot set

Update these first:

1. `current/STATE.md`
2. `current/tasks.csv`
3. `memory/PROJECT_FACTS.md`, only when a stable fact changed

Keep `memory/PROJECT_FACTS.md` within 80 lines and 4000 characters. Keep `current/STATE.md` within 80 lines and 4000 characters.

## Ledgers

Open `memory/LEDGER_INDEX.md`, then `## Summary` and `## Recent` of the one ledger you will append to. Do not load the archive tail unless that summary is not enough.

Append a short entry for a task change, a milestone, a decision, or a risk. Do not rewrite old decisions. Supersede them. Do not delete risks; mark them `mitigated`, `closed`, or `accepted`.

Leave worker outputs in `current/agent_outputs/` until phase close.

## Phase close

When every active task is `done` or `dropped`, or the user closes the phase:

1. Confirm the hot set and the ledger summaries mention the outcome.
2. Run `compact_memory.py --target <agent-group-path> --archive-name <yyyymmdd_topic> --dry-run`.
3. Apply the same command without `--dry-run`.
4. Expect new concise files in `current/`, and ledger overflow under `archive/ledgers/`.
5. Run `validate_agent_group.py --strict <agent-group-path>`.

`--no-reset-current` is only for a tool that immediately rebuilds the hot files. `--no-roll-ledgers` is only for a repair that must keep the hot ledger intact.

Do not archive `rules/`, `agents/`, or `memory/PROJECT_FACTS.md` with the phase.
