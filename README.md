# Agent Group Orchestrator

A backend-neutral plugin for project-local multi-agent orchestration in Claude Code and Codex.

## What It Does

- Initializes a project-local agent group workspace.
- Routes work through workers, task dependencies, and risk gates.
- Maintains current state, durable memory, and archived evidence.
- Reviews worker output and memory updates.

Runtime state stays in the target project:

- Claude Code: `.claude/agent_group/`
- Codex: `.codex/agent_group/`

## Execution Model

The default mode is `auto-orchestrate`. The `main-orchestrator` selects workers, manages the task DAG and risk gates, tracks progress, synchronizes memory, and reports results.

Every selected non-main worker must run through a compatible sub-agent backend. The main orchestrator does not perform worker-scoped implementation, testing, benchmarking, research, architecture, or review. If sub-agents are unavailable, the workflow is blocked.

## Installation

```bash
git clone https://github.com/BrokeDudeAbula/agent-group-orchestrator.git
cd agent-group-orchestrator
```

This checkout is a plugin root for both hosts, not a marketplace root.

Load it directly in Claude Code:

```bash
claude plugin validate /path/to/agent-group-orchestrator
claude --plugin-dir /path/to/agent-group-orchestrator
```

For persistent installation, reference the checkout from a registered local or team marketplace, then run the host command:

```bash
claude plugin install agent-group-orchestrator@personal
codex plugin add agent-group-orchestrator@personal
```

Start a new Claude Code session or Codex thread after installation.

## Quick Start

Run initialization from the target project root:

```bash
python3 /path/to/agent-group-orchestrator/scripts/init_agent_group.py \
  --backend codex \
  --project-name my-project
```

Use `--backend claude-code` for `.claude/agent_group/`, or `--target <path>` for an explicit location. Without `--target`, the resolver uses an existing standard instance or the backend default.

Validate the instance:

```bash
python3 /path/to/agent-group-orchestrator/scripts/validate_agent_group.py \
  --strict .codex/agent_group
```

Inspect path resolution:

```bash
python3 /path/to/agent-group-orchestrator/scripts/agent_group_paths.py \
  --backend auto \
  --json
```

After installation, trigger workflows with prompts such as:

```text
Initialize an agent group workspace for this repo.
Use agent-group auto-orchestrate mode for this goal: <goal>.
Validate this repo's agent group memory structure.
Review this agent group worker output and memory update.
```

## Project State

- `current/`: active goal, tasks, and worker evidence.
- `memory/`: durable task, progress, decision, risk, and project fact ledgers.
- `rules/`: routing, execution, memory, and runbook policies.
- `agents/`: worker role definitions.
- `archive/`: compacted historical evidence.

## Repository Layout

- `skills/`: initialization, orchestration, memory sync, and review workflows.
- `references/`: reusable policies, schemas, and contracts.
- `assets/templates/instance/`: the generic workspace template.
- `scripts/`: standard-library-only Python utilities.
- `examples/`: sample instances and regression fixtures.
- `.claude-plugin/` and `.codex-plugin/`: host manifests.

## Utilities

| Script | Purpose |
| --- | --- |
| `agent_group_paths.py` | Resolve the active workspace path. |
| `init_agent_group.py` | Create a workspace from the template. |
| `validate_agent_group.py` | Validate workspace structure and schemas. |
| `render_task_dag.py` | Render `tasks.csv` as Mermaid. |
| `compact_memory.py` | Archive current state and reset hot memory. |
| `check_public_safety.py` | Scan content and Git history for sensitive data. |

Run `compact_memory.py` with `--dry-run` before applying an archive operation.

## Development

There is no build step. Run the regression checks from the plugin root:

```bash
python3 -m unittest discover -s tests
python3 scripts/validate_agent_group.py --strict examples/sample
python3 scripts/check_public_safety.py --git-history .
claude plugin validate .
```

Run a fresh-instance smoke test when changing templates, initialization, or validation:

```bash
tmp_agent_group_root=$(mktemp -d)
python3 scripts/init_agent_group.py \
  --backend codex \
  --target "$tmp_agent_group_root/demo" \
  --project-name demo
python3 scripts/validate_agent_group.py --strict "$tmp_agent_group_root/demo"
```

## License

MIT. See [LICENSE](LICENSE).
