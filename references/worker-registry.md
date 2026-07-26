# Worker Registry Contract

Each worker entry should define:

- worker name
- `agent_file`
- selection triggers
- responsibilities
- permission boundary
- typical inputs
- required output shape

Worker names must match both the role file name and role frontmatter when frontmatter is present.

Each non-main worker entry is a sub-agent role. The main orchestrator uses the registry to choose and dispatch workers, but it must not perform the worker task itself. The worker `agent_file` is the role prompt that must be passed to the configured sub-agent backend.

Minimum recommended workers:

| Worker | Purpose |
|---|---|
| `main-orchestrator` | User-facing planner, task router, memory synchronizer |
| `repo-explorer` | Read-only codebase and artifact discovery |
| `perf-analyst` | Baseline, benchmark, profile, and evidence comparison |
| `oss-scout` | Open-source and upstream implementation research |
| `architect` or domain-specific architect | Design tradeoff analysis and implementation scope |
| `kernel-dev` or implementation worker | Scoped edits after write gate |
| `runner` or environment-specific runner | Builds, remote runs, profiling, or validation |
| `reviewer` | Checks evidence, regressions, permissions, and missing tests |

Instances can rename or remove workers, but the routing policy must stay synchronized with the registry.

The `main-orchestrator` supervises task assignment, progress, memory synchronization, evidence spot checks, and final reporting. It is not a fallback implementation, test, benchmark, research, architecture, or review worker.
