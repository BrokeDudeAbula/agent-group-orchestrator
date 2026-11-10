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

This file is the runtime worker registry. Do not also read the skill-pack worker reference.

Open it only when a role other than `repo-explorer` or `kernel-dev` is under consideration. Worker names match `agents/<worker-name>.md`. Pass that path to the sub-agent; do not paste the role file into the prompt.

## main-orchestrator

agent_file: `agents/main-orchestrator.md`

Plans, routes, performs cheap read-only R0/R1 lookups, syncs hot memory, and reports.

Permission: agent-group metadata and documentation. Ask before R3/R4. Do not perform a substantial worker task inline.

## repo-explorer

agent_file: `agents/repo-explorer.md`

Read-only discovery larger than a few named files.

Permission: read-only.

## kernel-dev

agent_file: `agents/kernel-dev.md`

Scoped edits after the write gate. This is the default implementer.

Permission: write only inside the approved scope.

## perf-analyst

agent_file: `agents/perf-analyst.md`

Measurements and evidence comparison. Skip unless the goal is a performance claim.

Permission: read-only unless explicitly gated.

## oss-scout

agent_file: `agents/oss-scout.md`

Upstream and open-source research. Skip unless the goal needs that comparison.

Permission: read-only research.

## architect

agent_file: `agents/architect.md`

Design comparison before editing. Skip unless several options must be compared.

Permission: read-only.

## runner

agent_file: `agents/runner.md`

Gated builds, tests, profiling, or remote validation.

Permission: gated execution.

## reviewer

agent_file: `agents/reviewer.md`

Review when the user asked, evidence is disputed, or the next step is R3/R4. Do not add a reviewer by default.

Permission: read-only by default.
