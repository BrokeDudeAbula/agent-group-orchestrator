---
ag_schema: v1
doc_id: AG-RULE-RUNBOOK-REMOTE
category: rules
doc_type: remote_runbook
authority: template
lifecycle: warm
read_policy: on_demand
write_policy: controlled_update
risk_level: R4
owner: runner
---

# Remote Runbook

Use this template only when the project needs remote, long-running, or expensive validation.

Before R4 execution, record:

- target host or service
- command
- expected duration
- output directory
- stop condition
- rollback or cleanup expectation

The runner must report commands, environment, artifacts, pass/fail status, and blockers.

