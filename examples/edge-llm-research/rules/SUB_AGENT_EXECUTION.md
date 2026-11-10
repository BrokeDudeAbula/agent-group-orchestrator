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

This rule applies whenever an agent group workflow selects a worker other than `main-orchestrator`.

## Core Rule

The `main-orchestrator` is a supervisor, not a worker executor. It must coordinate the workflow, but it must not directly perform implementation, testing, benchmarking, code review, open-source research, repository discovery, or architecture tasks.

Every selected worker task must be dispatched to a sub-agent that runs with the selected worker role and receives the relevant task id, scope, inputs, risk boundary, and output contract.

If no compatible sub-agent backend is available, report the workflow as blocked or ask the user to switch to a backend that supports sub-agents. Do not silently complete worker tasks in the main orchestrator.

## Backend Compatibility

The workflow is backend-neutral and must support the host's available sub-agent mechanism.

- Claude Code CLI: create one sub-agent per selected worker task using the available Claude Code CLI sub-agent mechanism.
- Codex: create one sub-agent per selected worker task using the available Codex sub-agent or multi-agent primitive.
- Cursor, OpenCode, Grok Build, and similar hosts: create one sub-agent per selected worker task with that host's sub-agent mechanism, and record the host name.

Every backend must receive the same worker role file, task id, scope, dependency outputs, risk boundary, expected output path, and output contract.

## Main Orchestrator Duties

The main orchestrator may:

- clarify user goals and acceptance criteria;
- classify risk and request R3/R4 gates;
- select workers and maintain the task DAG;
- dispatch worker prompts to sub-agents;
- monitor progress, retries, and blockers;
- synchronize `current/` state and durable memory;
- spot-check worker evidence;
- summarize results, risks, and next steps.

The main orchestrator must not:

- write implementation patches for `kernel-dev`;
- run tests, benchmarks, profilers, or remote commands for `runner`;
- produce primary repository analysis for `repo-explorer`;
- produce primary performance analysis for `perf-analyst`;
- produce primary upstream research for `oss-scout`;
- produce primary design analysis for `architect`;
- act as the final `reviewer` for its own orchestration result.

## Scheduling Rules

- Respect dependencies in `current/tasks.csv`.
- Dispatch independent workers concurrently when the backend supports parallel sub-agents.
- If the backend only supports serialized sub-agents, execute the DAG serially while still using sub-agents.
- Stop before R3/R4 work until the user grants the required gate.
- On sub-agent failure, mark the task as `blocked` or retry with a narrowed prompt; record the reason and evidence path.

## Worker Prompt Minimums

Each sub-agent prompt must include:

- task id and title;
- selected worker name and `agents/<worker>.md` role file;
- scope, inputs, and expected artifacts;
- dependency outputs to read;
- risk level and permission boundary;
- required output path under `current/agent_outputs/`;
- output contract headings;
- stop condition and escalation rule.

## Evidence Requirements

Each worker output should identify:

- execution backend, for example `claude-code-cli`, `codex`, or another host name;
- sub-agent reference, if the backend provides one;
- whether the worker ran concurrently or serially;
- inputs read, commands run, artifacts produced, blockers, and recommended next step.

The final report should list workers selected, workers skipped, sub-agent references, evidence checked, memory updates, and remaining risks.
