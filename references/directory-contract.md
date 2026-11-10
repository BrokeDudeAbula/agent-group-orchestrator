# Directory Contract

An agent group instance is a project-local coordination workspace. Supported standard target paths are:

```text
.agent_group/           # host-neutral default for Cursor, OpenCode, Grok Build, and similar hosts
.claude/agent_group/    # Claude Code
.codex/agent_group/     # Codex
```

Resolve the active instance in this order:

1. Explicit path from the user or CLI `--target`.
2. An existing standard instance under the project root.
3. Host default when no instance exists yet.
4. Ask the user if more than one standard instance exists and no path was specified.

The instance body is backend-neutral. Only the parent directory differs by host.

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
rules/SUB_AGENT_EXECUTION.md
rules/MEMORY_SYNC_SOP.md
memory/LEDGER_INDEX.md
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
execution_backend: auto
task_id_prefix: AUTO
worker_output_dir: current/agent_outputs
archive_dir: archive
```

Recommended `current/tasks.csv` header:

```text
id,title,owner,status,risk,depends_on,inputs,outputs,notes
```

Rules:

- `rules/` is the runtime policy. Do not also load the skill-pack `references/` copy of the same topic.
- `memory/` stores durable project memory. `memory/LEDGER_INDEX.md` is the door to the ledgers. `memory/PROJECT_FACTS.md` stays compact enough to read on an orchestrate turn.
- `current/` stores the active epic, active task list, hot state, and worker outputs.
- `agents/` stores worker role definitions.
- `archive/` stores compacted `current/` evidence and rolled ledger tails under `archive/ledgers/`.
- Skill pack templates must not contain live user project secrets or one-off local paths.
- The default DAG is `repo-explorer`, then `kernel-dev` when a change is required. Other workers need a reason.
- The main orchestrator may do cheap read-only R0/R1 lookups itself. Substantial non-main work goes to a sub-agent with a short upstream summary and file paths, not full upstream outputs.
