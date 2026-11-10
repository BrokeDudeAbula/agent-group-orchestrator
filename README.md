# Agent Group Orchestrator

A portable skill pack for project-local multi-agent orchestration. One skill routes initialization, orchestration, memory sync, and review. Runtime state stays in the target project.

## What It Does

- Initializes a project-local agent group workspace.
- Routes work through workers, task dependencies, and risk gates.
- Maintains current state, durable memory, and archived evidence.
- Reviews worker output and memory updates.

Runtime state stays in the target project:

- Cursor, OpenCode, Grok Build, and similar hosts: `.agent_group/`
- Claude Code: `.claude/agent_group/`
- Codex: `.codex/agent_group/`

## Execution Model

The default mode is `auto-orchestrate`. The `main-orchestrator` selects workers, manages the task DAG and risk gates, tracks progress, synchronizes memory, and reports results.

Every selected non-main worker must run through a compatible sub-agent backend. The main orchestrator does not perform worker-scoped implementation, testing, benchmarking, research, architecture, or review. If sub-agents are unavailable, the workflow is blocked.

## Installation

Copy this checkout into a host skills directory and name that directory `agent-group`, matching the `name` in `SKILL.md`. The copy must include `SKILL.md`, `workflows/`, `scripts/`, `references/`, and `assets/`.

```bash
git clone https://github.com/BrokeDudeAbula/agent-group-orchestrator.git
mkdir -p ~/.claude/skills
cp -R agent-group-orchestrator ~/.claude/skills/agent-group
```

Claude Code also loads a project skill from `.claude/skills/agent-group/`. Use the same directory copy for the other hosts:

| Host | User skills path | Project skills path |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/agent-group/` | `.claude/skills/agent-group/` |
| Cursor | `~/.cursor/skills/agent-group/` | `.cursor/skills/agent-group/` or `.agents/skills/agent-group/` |
| Codex | `~/.agents/skills/agent-group/` | `.agents/skills/agent-group/` |
| OpenCode | `~/.config/opencode/skills/agent-group/` | `.opencode/skills/agent-group/` |
| Grok Build | `~/.grok/skills/agent-group/` | `.grok/skills/agent-group/` |

Start a new session after copying the skill. Several hosts also read `~/.agents/skills/`; that user path is a portable place for the same directory.

## Quick Start

Run initialization from the target project root:

```bash
python3 /path/to/agent-group/scripts/init_agent_group.py \
  --project-name my-project
```

Without `--target`, the resolver uses an existing standard instance when only one is present. Otherwise it uses the host default: `.claude/agent_group/` on Claude Code, `.codex/agent_group/` on Codex, and `.agent_group/` for other hosts. Pass `--backend claude-code`, `--backend codex`, `--backend neutral`, or `--target <path>` to choose explicitly.

Validate the instance:

```bash
python3 /path/to/agent-group/scripts/validate_agent_group.py \
  --strict .agent_group
```

Inspect path resolution:

```bash
python3 /path/to/agent-group/scripts/agent_group_paths.py \
  --backend auto \
  --json
```

After installation, trigger the skill with prompts such as:

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

- `SKILL.md`: the skill entry. It routes by intent to a workflow.
- `workflows/`: initialization, orchestration, memory sync, and review.
- `references/`: reusable policies, schemas, and contracts.
- `assets/templates/instance/`: the generic workspace template.
- `scripts/`: standard-library-only Python utilities.
- `examples/`: sample instances and regression fixtures.

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

There is no build step. Run the regression checks from the skill pack root:

```bash
python3 -m unittest discover -s tests
python3 scripts/validate_agent_group.py --strict examples/sample
python3 scripts/check_public_safety.py --git-history .
```

Run a fresh-instance smoke test when changing templates, initialization, or validation:

```bash
tmp_agent_group_root=$(mktemp -d)
python3 scripts/init_agent_group.py \
  --backend claude-code \
  --root "$tmp_agent_group_root" \
  --project-name demo
python3 scripts/validate_agent_group.py --strict "$tmp_agent_group_root/.claude/agent_group"

tmp_neutral_root=$(mktemp -d)
python3 scripts/init_agent_group.py \
  --backend neutral \
  --root "$tmp_neutral_root" \
  --project-name demo
python3 scripts/validate_agent_group.py --strict "$tmp_neutral_root/.agent_group"
```

## License

MIT. See [LICENSE](LICENSE).
