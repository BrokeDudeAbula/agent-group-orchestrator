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
4. Verify that each non-main worker output was produced by a sub-agent and records the execution backend and sub-agent reference when available.
5. Check that the main orchestrator stayed in a supervisory role and did not directly perform worker-scoped implementation, testing, benchmarking, research, architecture, or review work.
6. Check the risk level and whether required user gates were honored.
7. Check memory updates for consistency across `current/tasks.csv`, `current/STATE.md`, and durable ledgers.
8. Report findings first, ordered by severity, with file links when possible.

## Review Focus

- Unsupported performance or correctness claims.
- Missing baseline or non-comparable measurements.
- Worker operating outside its permission boundary.
- Missing sub-agent backend or sub-agent reference for non-main worker output.
- Main orchestrator replacing a worker instead of dispatching and supervising a sub-agent.
- R3/R4 actions without a gate.
- Task status inconsistent with evidence.
- Lost or unarchived worker outputs.
