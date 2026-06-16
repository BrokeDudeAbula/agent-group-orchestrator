---
name: agent-group-review
description: Use when Codex should review an agent group workflow, worker output, routing decision, memory update, or task evidence for correctness, missing validation, and risk.
---

# Agent Group Review

Use this skill for review gates inside an agent group workflow.

## Workflow

1. Identify the task id and relevant worker outputs.
2. Check the output against `references/output-contract.md`.
3. Verify that conclusions are supported by files, commands, or reports.
4. Check the risk level and whether required user gates were honored.
5. Check memory updates for consistency across `current/tasks.csv`, `current/STATE.md`, and durable ledgers.
6. Report findings first, ordered by severity, with file links when possible.

## Review Focus

- Unsupported performance or correctness claims.
- Missing baseline or non-comparable measurements.
- Worker operating outside its permission boundary.
- R3/R4 actions without a gate.
- Task status inconsistent with evidence.
- Lost or unarchived worker outputs.

