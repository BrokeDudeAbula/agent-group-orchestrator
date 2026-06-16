# Risk Policy

Use this default risk model when an instance does not define a stricter one.

| Level | Meaning | Default handling |
|---|---|---|
| R0 | Read-only inspection | Can proceed automatically |
| R1 | Agent-group metadata or documentation writes | Can proceed automatically and report files changed |
| R2 | Non-core project docs, scripts, or reports | Proceed when write scope is explicit; otherwise ask |
| R3 | Core source, build, CUDA, database, deployment, or production behavior changes | Ask for confirmation of write scope before editing |
| R4 | Remote machines, long builds, profiling, destructive operations, cost-incurring actions | Ask for command, duration, outputs, and stop condition |

When in doubt, raise the risk level. The point of the gate is to protect project state, hardware time, and evidence integrity.

