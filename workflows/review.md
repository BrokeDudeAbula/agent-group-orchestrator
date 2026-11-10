# Agent Group Review

Use this workflow for a review gate. Do not run it on a normal orchestrate turn unless a review was requested or a task note records why a reviewer is required.

`<skill-root>` is the directory that contains `SKILL.md`. Task files and worker outputs are inside the target instance.

## Working set

Read the task row in `current/tasks.csv`, `current/STATE.md`, and the worker output under review. Open other files only when a finding depends on them. Do not load upstream outputs in full when the output under review already links them.

## Workflow

1. Identify the task id and the relevant worker output.
2. Run strict validation and treat failures as findings:

```bash
python3 <skill-root>/scripts/validate_agent_group.py --strict <agent-group-path>
```

3. Check that conclusions cite files, commands, or reports, and that the output stays within 120 lines and 6000 characters.
4. A substantial non-main worker output records an execution backend and a sub-agent reference when the backend provides one. Cheap read-only R0/R1 lookups may stay in the main session and do not need a sub-agent.
5. Check the risk level and whether required user gates were honored.
6. Check `current/tasks.csv` and `current/STATE.md` against the evidence. Open a ledger only through `memory/LEDGER_INDEX.md` when a finding depends on an older decision or risk.
7. Report findings first, ordered by severity, with file links.

## Review Focus

- Unsupported performance or correctness claims.
- Missing baseline or non-comparable measurements.
- Worker operating outside its permission boundary.
- A substantial worker task completed in the main session instead of a sub-agent.
- R3/R4 actions without a gate.
- Task status inconsistent with evidence.
- Lost or unarchived worker outputs.
- Worker output that pastes logs instead of linking them.
