# Memory Sync SOP

Runtime copy: the instance file `rules/MEMORY_SYNC_SOP.md`.
Load this reference only when that file does not exist. Do not load both.

An orchestrate turn reads `current/STATE.md`, `current/tasks.csv`, and `memory/PROJECT_FACTS.md`. Durable ledgers are reached through `memory/LEDGER_INDEX.md`, then `## Summary` and `## Recent` of one ledger.

## Update order

1. Update `current/STATE.md`.
2. Update `current/tasks.csv`.
3. Update `memory/PROJECT_FACTS.md` when a stable fact changed. Keep it within 80 lines and 4000 characters.
4. Append a short entry to the one ledger that changed. Read its summary and recent tail first, not the archive.
5. Leave raw worker outputs in `current/agent_outputs/` until phase close.

Do not delete decisions or risks. Supersede decisions. Mark risks `mitigated`, `closed`, or `accepted`.

## Phase close

Run `compact_memory.py` with `--dry-run`, then without it. The helper archives `current/` and recreates the hot files. Ledger files that exceed the roll threshold are rewritten to a bounded summary plus recent tail. Older text is appended under `archive/ledgers/`. Rules, agent roles, and `memory/PROJECT_FACTS.md` are not archived that way.

Use `--no-reset-current` only when another tool will immediately rebuild the hot files. Use `--no-roll-ledgers` only when ledger history must stay in the hot file for a repair.
