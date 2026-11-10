---
ag_schema: v1
doc_id: AG-RULE-SUB-AGENT-EXECUTION
category: rules
doc_type: sub_agent_execution
authority: canonical
lifecycle: warm
read_policy: on_demand
write_policy: controlled_update
risk_level: R1
owner: main-orchestrator
---

# Sub-Agent Execution

This file is the runtime execution rule. Do not also read the skill-pack sub-agent reference. Open it when dispatching a sub-agent.

## Core Rule

Substantial work for any worker other than `main-orchestrator` goes to one sub-agent. If no sub-agent backend is available, mark the workflow blocked.

The main orchestrator may do cheap read-only R0/R1 work itself: a few named-file lookups, a narrow question, evidence spot checks, and its own memory updates. That does not replace discovery, implementation, measurement, upstream research, design comparison, test runs, or formal review.

## Prompt

Pass the task id, worker name, path `agents/<worker>.md`, scope, risk, output path, and stop condition. Pass upstream results as a few sentences plus file paths. Do not paste upstream outputs, the role file, or policy documents. The sub-agent reads the paths.

## Scheduling

- Respect `depends_on` in `current/tasks.csv`.
- Independent tasks may run concurrently when the host supports it.
- Stop before R3/R4 until the user grants the gate.
- On failure, mark the task `blocked` or retry with a narrower prompt.

## Evidence

Record the host name and any sub-agent reference. Keep the worker output within 120 lines and 6000 characters.
