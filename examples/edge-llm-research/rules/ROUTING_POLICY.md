---
ag_schema: v1
doc_id: AG-RULE-ROUTING-POLICY
category: rules
doc_type: routing_policy
authority: canonical
lifecycle: warm
read_policy: on_demand
write_policy: controlled_update
risk_level: R1
owner: main-orchestrator
---

# Routing Policy

This file is the runtime routing policy. Do not also read the skill-pack routing reference.

Open it only when the default DAG is not enough.

## Default DAG

```text
repo-explorer -> kernel-dev
```

A read-only goal stops after `repo-explorer`. The main orchestrator writes the report.

## Extra workers

Add one of these only with a reason in the task notes:

| Worker | Reason |
| --- | --- |
| `perf-analyst` | The goal is a measurement or performance claim |
| `oss-scout` | The goal needs upstream or ecosystem comparison |
| `architect` | Several designs must be compared before editing |
| `reviewer` | The user asked for review, evidence is disputed, or the next step is R3/R4 |
| `runner` | A gated build, test, or remote validation is required |

## Edge LLM competitor research

Use this DAG only when the goal asks for research on LLM inference engines, operator strategies, inference acceleration, benchmark comparability, timing semantics, or an optimization roadmap:

```text
repo-explorer -> oss-scout -> perf-analyst -> architect -> reviewer
```

Record that reason on the task notes. `kernel-dev` and `runner` stay out until the user asks to implement a roadmap item or grants an R4 run.

Cheap read-only R0/R1 lookups stay in the main session. Do not spawn a sub-agent to read a few named files.

## Dispatch

A substantial non-main task is one sub-agent. Open `rules/SUB_AGENT_EXECUTION.md` for the prompt shape. Pass a short upstream summary and file paths, not full upstream outputs. If sub-agents are unavailable, mark the workflow blocked.

## Risk

Use the risk summary in `rules/BOOTSTRAP.md`. R3 and R4 wait for an explicit user gate.

## Task naming

```text
ELLM-<yyyymmdd>-<nn>
```

Record dependencies in `current/tasks.csv` with `depends_on`, separated by semicolons.

## Worker outputs

```text
current/agent_outputs/<task_id>_<worker>.md
```

Keep each output within 120 lines and 6000 characters. Link evidence instead of pasting logs.
