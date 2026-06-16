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

## current/tasks.csv

Purpose: active epic task list.

Required columns:

```text
id,title,owner,status,risk,inputs,outputs,notes
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
- scope
- inputs read
- commands run, if any
- conclusion
- artifacts
- risks or blockers
- recommended next step

## memory/TASK_LEDGER.md

Purpose: durable task history.

Recommended entry fields:

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

Purpose: stable project facts.

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

