# Directory Contract

An agent group instance is a project-local coordination workspace. The default target path is:

```text
.codex/agent_group/
```

Required directories:

```text
agent_group/
├── rules/
├── memory/
├── current/
├── current/agent_outputs/
├── agents/
└── archive/
```

Required files:

```text
rules/BOOTSTRAP.md
rules/WORKER_REGISTRY.md
rules/ROUTING_POLICY.md
rules/MEMORY_SYNC_SOP.md
memory/TASK_LEDGER.md
memory/PROGRESS_LEDGER.md
memory/DECISIONS.md
memory/RISKS.md
memory/PROJECT_FACTS.md
current/STATE.md
current/epic.md
current/acceptance.md
current/tasks.csv
```

Recommended instance config:

```yaml
project_name: example
default_mode: auto-orchestrate
task_id_prefix: AUTO
worker_output_dir: current/agent_outputs
archive_dir: archive
```

Recommended `current/tasks.csv` header:

```text
id,title,owner,status,risk,depends_on,inputs,outputs,notes
```

Rules:

- `rules/` stores durable operating policy.
- `memory/` stores durable project memory and append-only ledgers.
- `current/` stores the active epic, active task list, hot state, and worker outputs.
- `agents/` stores worker role definitions.
- `archive/` stores compacted historical evidence.
- Plugin templates must not contain live user project secrets or one-off local paths.
