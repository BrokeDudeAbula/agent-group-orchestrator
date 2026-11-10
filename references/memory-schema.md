# Memory Schema

This schema defines the expected shape of a project-local agent group instance. The validator supports a minimal mode and a stricter mode. The strict mode should enforce the structures below where practical.

## current/STATE.md

Purpose: hot state for fast context recovery.

Required headings:

```text
# Current State
## Active Goal
## Current Phase
## Active Task
## Blockers
## Latest Evidence
## Next Step
```

Rules:

- Keep it concise.
- Store only current state, not full history.
- Link to worker outputs or archive paths instead of pasting long logs.
- Strict validation rejects a state file over 80 lines or 4000 characters.

## current/tasks.csv

Purpose: active epic task list.

Required columns:

```text
id,title,owner,status,risk,inputs,outputs,notes
```

Recommended columns for DAG-aware instances:

```text
id,title,owner,status,risk,depends_on,inputs,outputs,notes
```

Allowed `status` values:

```text
todo
in_progress
blocked
review
done
dropped
```

Recommended `risk` values:

```text
R0
R1
R2
R3
R4
```

Rules:

- Keep only the active epic in `current/tasks.csv`.
- Use `depends_on` for task ids that must complete before the current task. Separate multiple dependencies with semicolons.
- Move completed phase evidence into `archive/`.
- Use durable ledgers for cross-epic history.

## current/agent_outputs/

Purpose: raw worker outputs for the current phase.

Recommended filename:

```text
<task_id>_<worker>.md
```

Each output should include:

- task id
- worker name
- execution backend, for example `claude-code-cli` or `codex`
- sub-agent reference, if the backend provides one
- scope
- inputs read
- commands run, if any
- conclusion
- artifacts
- risks or blockers
- recommended next step

Strict and non-strict validation reject an output over 120 lines or 6000 characters. Link evidence instead of pasting logs.

Strict validation expects these Markdown headings:

```text
## Task ID
## Worker Name
## Execution Backend
## Sub-Agent Reference
## Scope
## Inputs Read
## Commands Run
## Conclusion
## Artifacts
## Risks or Blockers
## Recommended Next Step
```

## memory/LEDGER_INDEX.md

Purpose: the only door to durable ledgers on a normal turn.

Rules:

- Keep it within 40 lines and 2500 characters.
- Name `TASK_LEDGER.md`, `PROGRESS_LEDGER.md`, `DECISIONS.md`, and `RISKS.md`.
- Tell the reader which ledger to open, and to read `## Summary` and `## Recent` only.

## memory/TASK_LEDGER.md

Purpose: durable task history.

Required heading: `## Summary`.

Hot shape:

```text
## Summary
## Recent
```

Strict validation rejects a ledger over 80 lines or 6000 characters. `compact_memory.py` rolls a ledger that passes 48 lines or 3500 characters. The hot file keeps a short summary and a recent tail. Older text is appended to `archive/ledgers/<ledger>.md`.

The same summary, recent tail, and roll rule apply to `memory/PROGRESS_LEDGER.md`, `memory/DECISIONS.md`, and `memory/RISKS.md`.

Recommended task entry fields:

- task id
- title
- owner
- status
- risk
- scope
- inputs
- outputs
- acceptance
- latest update

## memory/PROGRESS_LEDGER.md

Purpose: append-only progress summary.

Recommended entry fields:

- date
- task id or milestone
- summary
- artifacts
- blockers
- next step

## memory/DECISIONS.md

Purpose: append-only decision log.

Recommended entry fields:

- decision id
- date
- status
- context
- decision
- rationale
- consequences
- supersedes, if any

Rules:

- Do not delete historical decisions.
- Add a new decision when superseding an old one.

## memory/RISKS.md

Purpose: risk register.

Recommended entry fields:

- risk id
- status: `active`, `mitigated`, `closed`, or `accepted`
- owner
- trigger
- impact
- mitigation
- latest update

Rules:

- Do not remove risks to hide history.
- Update status and mitigation instead.

## memory/PROJECT_FACTS.md

Purpose: stable project facts read on an orchestrate turn.

Strict validation rejects this file over 80 lines or 4000 characters. Compaction does not archive it. Trim stale facts in place.

Recommended sections:

- repository layout
- important entrypoints
- build and validation commands
- external dependencies
- environment assumptions
- known stale or uncertain facts

## archive/

Purpose: compacted historical evidence.

Recommended archive directory:

```text
archive/<yyyymmdd_topic>/
```

Recommended contents:

```text
STATE.md
epic.md
acceptance.md
tasks.csv
agent_outputs/
```

Rolled ledger tails are appended under `archive/ledgers/` and are not part of the phase directory.
