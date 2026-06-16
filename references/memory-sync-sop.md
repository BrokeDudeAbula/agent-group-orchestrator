# Memory Sync SOP

After a task or milestone, synchronize memory in this order:

1. Update `current/STATE.md` with active goal, phase, blockers, latest evidence, and next step.
2. Update `current/tasks.csv` for active task status changes.
3. Append durable task changes to `memory/TASK_LEDGER.md`.
4. Append progress to `memory/PROGRESS_LEDGER.md`.
5. Append decisions to `memory/DECISIONS.md`; do not rewrite old decisions except to mark supersession clearly.
6. Update `memory/RISKS.md` by status, owner, trigger, and mitigation.
7. Keep raw worker evidence in `current/agent_outputs/` until compaction.

Compaction rules:

- Archive old `current/` evidence before resetting it.
- Keep long-lived project facts, decisions, risks, and roadmap material in `memory/`.
- Do not hide blockers by deleting them; mark them closed, mitigated, accepted, or superseded.
- Prefer `compact_memory.py --dry-run` before moving files.

