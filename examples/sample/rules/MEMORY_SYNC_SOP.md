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

Before compaction or epic handoff, apply the memory lifecycle rules:

- Sync reusable conclusions to `memory/` before moving hot state.
- Keep durable project facts, decisions, risks, and ledgers in `memory/`; do not archive them with phase evidence.
- Do not delete blockers or risks; close, mitigate, accept, or supersede them.

## Normal Update

1. Update `current/STATE.md`.
2. Update `current/tasks.csv`.
3. Append to `memory/TASK_LEDGER.md` when task status or scope changes.
4. Append to `memory/PROGRESS_LEDGER.md` after meaningful progress.
5. Append to `memory/DECISIONS.md` for durable decisions.
6. Update `memory/RISKS.md` for active, mitigated, closed, or accepted risks.
7. Update `memory/PROJECT_FACTS.md` for stable facts, important entrypoints, commands, dependencies, and environment assumptions.
8. Keep worker evidence in `current/agent_outputs/`.

## Compaction

1. Confirm `current/STATE.md`, `current/tasks.csv`, worker outputs, and durable ledgers are synchronized.
2. Run `compact_memory.py --target <agent-group-path> --archive-name <yyyymmdd_topic> --dry-run`.
3. Review the move plan.
4. Run without `--dry-run` when the archive should be applied.
5. Confirm the script recreated concise `current/STATE.md`, `current/epic.md`, `current/acceptance.md`, and `current/tasks.csv`.
6. Append the compaction event and archive path to `memory/PROGRESS_LEDGER.md`.
7. Run `validate_agent_group.py --strict <agent-group-path>`.

Use `--no-reset-current` only when another tool will immediately rebuild the required hot state files.
