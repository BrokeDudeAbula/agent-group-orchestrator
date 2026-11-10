# Sub-Agent Execution Contract

Runtime copy: the instance file `rules/SUB_AGENT_EXECUTION.md`.
Load this reference only when that file does not exist. Do not load both.

## Core Rule

Substantial work for a worker other than `main-orchestrator` goes to one sub-agent with that worker's role. If no sub-agent backend is available, report the workflow as blocked.

The main orchestrator may do cheap read-only R0/R1 work itself: a few named-file lookups, a narrow question, evidence spot checks, and its own memory updates. That work is not a substitute for `repo-explorer`, `kernel-dev`, `perf-analyst`, `oss-scout`, `architect`, `runner`, or `reviewer`.

The main orchestrator must not write implementation patches, run tests or benchmarks, produce the primary repository or design analysis, or act as the formal reviewer for its own result.

## Prompt

Pass:

- task id and title
- worker name and the path `agents/<worker>.md`
- scope, risk level, and permission boundary
- a short summary of upstream results, plus file paths
- output path under `current/agent_outputs/`
- stop condition

Do not paste full upstream outputs, role files, or policy documents into the prompt. The sub-agent reads the paths.

## Backend

Use the host's sub-agent mechanism. Claude Code, Codex, Cursor, OpenCode, Grok Build, and similar hosts each dispatch one sub-agent per selected worker task. Record the host name and any sub-agent reference the host provides.

Respect `current/tasks.csv` dependencies. Independent tasks may run concurrently when the host supports it. Stop before R3/R4 work until the user grants the gate. On failure, mark the task `blocked` or retry with a narrower prompt.

## Evidence

Each worker output names the execution backend, the sub-agent reference when one exists, the inputs read, commands run, artifacts, blockers, and the next step. Keep it within 120 lines and 6000 characters.
