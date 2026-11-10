# Worker Registry Contract

Runtime copy: the instance file `rules/WORKER_REGISTRY.md`.
Load this reference only when that file does not exist. Do not load both.

The default DAG uses `repo-explorer` and `kernel-dev`. Other workers are optional and need a reason in the task notes.

| Worker | Purpose |
| --- | --- |
| `main-orchestrator` | Plan, route, do cheap R0/R1 lookups, sync hot memory, report |
| `repo-explorer` | Read-only discovery that is larger than a few named files |
| `kernel-dev` | Scoped edits after the write gate |
| `perf-analyst` | Measurement and evidence comparison |
| `oss-scout` | Upstream and open-source research |
| `architect` | Design comparison before editing |
| `runner` | Gated builds, tests, profiling, or remote validation |
| `reviewer` | Review when the user asked, evidence is disputed, or the next step is R3/R4 |

Worker names match `agents/<worker>.md`. The main orchestrator passes that path to the sub-agent. It does not perform a substantial worker task itself.
