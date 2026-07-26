# Sub-Agent Execution Contract

This contract applies whenever an agent group workflow selects a worker other than `main-orchestrator`.

## Core Rule

The `main-orchestrator` is a supervisor, not a worker executor. It must coordinate the workflow, but it must not directly perform implementation, testing, benchmarking, code review, open-source research, or other worker-scoped tasks.

Every selected worker task must be dispatched to a sub-agent that runs with the selected worker role and receives the relevant task id, scope, inputs, risk boundary, and output contract.

If no compatible sub-agent backend is available, the main orchestrator must report the workflow as blocked or ask the user to switch to a backend that supports sub-agents. It must not silently complete worker tasks itself.

## Main Orchestrator Duties

The main orchestrator may:

- clarify the user goal and acceptance criteria;
- classify risk and request R3/R4 gates;
- select workers from the registry;
- build and maintain the task DAG;
- dispatch worker prompts to sub-agents;
- monitor progress, retries, and blockers;
- synchronize `current/` state and durable memory;
- inspect a sample of worker evidence for plausibility;
- compare worker outputs against the acceptance criteria;
- summarize results, risks, and next steps for the user.

The main orchestrator must not:

- write implementation patches for a `kernel-dev` task;
- run tests, benchmarks, profilers, or remote commands for a `runner` task;
- produce the primary repository analysis for a `repo-explorer` task;
- produce the primary performance analysis for a `perf-analyst` task;
- produce the primary upstream research for an `oss-scout` task;
- produce the primary design analysis for an `architect` task;
- act as the final `reviewer` for its own orchestration result.

Small read-only checks are allowed only for routing, progress supervision, memory synchronization, or evidence spot-checking. They must not replace the assigned worker output.

## Backend Adapter Requirements

The execution model is backend-neutral. Each backend adapter must preserve the same worker contract and output shape.

### Claude Code CLI

Use the available Claude Code CLI sub-agent mechanism to create one sub-agent per selected worker task. Pass the selected `agents/<worker>.md` role, task id, risk gate, inputs, expected output path, and output contract to the sub-agent.

Record the Claude Code CLI sub-agent reference, such as a session id, agent id, transcript path, command log path, or other available handle, in the worker output or orchestrator report.

### Codex

Use the available Codex sub-agent or multi-agent primitive to create one sub-agent per selected worker task. Pass the same worker role, task id, risk gate, inputs, expected output path, and output contract.

Record the Codex sub-agent reference, such as a thread id, run id, task id, or other available handle, in the worker output or orchestrator report.

## Scheduling Rules

- Respect `current/tasks.csv` dependencies before dispatching a worker.
- Dispatch independent workers concurrently when the backend supports parallel sub-agents.
- If the backend only supports serialized sub-agents, execute the same DAG order serially while still using sub-agents.
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
- the output contract headings;
- stop condition and escalation rule.

## Evidence Requirements

Each worker output should identify:

- execution backend, for example `claude-code-cli` or `codex`;
- sub-agent reference, if the backend provides one;
- whether the worker ran concurrently or serially;
- inputs read, commands run, artifacts produced, blockers, and recommended next step.

The main orchestrator final report should list workers selected, workers skipped, sub-agent references, evidence checked, memory updates, and remaining risks.
