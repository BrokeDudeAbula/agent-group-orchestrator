---
ag_schema: v1
doc_id: AG-RULE-WORKER-REGISTRY
category: rules
doc_type: worker_registry
authority: canonical
lifecycle: warm
read_policy: on_demand
write_policy: controlled_update
risk_level: R1
owner: main-orchestrator
---

# Worker Registry

Worker names must match `agents/<worker-name>.md`.

Each non-main worker entry is a sub-agent role. The main orchestrator selects and dispatches workers, but it must not perform the worker task itself. Pass the matching `agents/<worker-name>.md` role file to the Codex or Claude Code CLI sub-agent backend.

## main-orchestrator

agent_file: `agents/main-orchestrator.md`

Use for user communication, task decomposition, DAG construction, sub-agent dispatch, progress supervision, evidence spot checks, risk gates, memory synchronization, and final reporting.

Permission: may write agent-group metadata and documentation; ask before R3/R4 work. Must not directly perform non-main worker tasks.

## repo-explorer

agent_file: `agents/repo-explorer.md`

Use for read-only repository, artifact, report, script, and call-chain discovery.

Permission: read-only.

## perf-analyst

agent_file: `agents/perf-analyst.md`

Use for benchmark, baseline, latency, throughput, profiling, and evidence-comparison tasks.

Permission: read-only unless explicitly gated.

## oss-scout

agent_file: `agents/oss-scout.md`

Use for upstream, open-source, official-doc, issue, paper, or implementation comparison.

Permission: read-only research.

## architect

agent_file: `agents/architect.md`

Use for option analysis, design planning, implementation scope, validation strategy, and risk assessment.

Permission: read-only.

## kernel-dev

agent_file: `agents/kernel-dev.md`

Use for scoped implementation or documentation edits after the main orchestrator defines write scope.

Permission: write only inside approved scope.

## runner

agent_file: `agents/runner.md`

Use for build, test, benchmark, profiling, or remote validation after required gates.

Permission: gated execution.

## reviewer

agent_file: `agents/reviewer.md`

Use for evidence review, regression risk, missing tests, permission boundary checks, and final gate review.

Permission: read-only by default.
