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

## Normal Update

1. Update `current/STATE.md`.
2. Update `current/tasks.csv`.
3. Append to `memory/TASK_LEDGER.md` when task status or scope changes.
4. Append to `memory/PROGRESS_LEDGER.md` after meaningful progress.
5. Append to `memory/DECISIONS.md` for durable decisions.
6. Update `memory/RISKS.md` for active, mitigated, closed, or accepted risks.
7. Keep worker evidence in `current/agent_outputs/`.

## Compaction

1. Create `archive/<yyyymmdd_topic>/`.
2. Move old `current/` files and worker outputs into the archive.
3. Recreate a concise `current/STATE.md`.
4. Recreate active `current/tasks.csv` for the new epic.
5. Append the compaction event to `memory/PROGRESS_LEDGER.md`.

Use `compact_memory.py --dry-run` before applying moves.

