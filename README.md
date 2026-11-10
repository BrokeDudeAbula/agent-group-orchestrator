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

The default mode is `auto-orchestrate`. A normal turn reads one workflow, `rules/BOOTSTRAP.md`, `current/STATE.md`, `current/tasks.csv`, and the compact `memory/PROJECT_FACTS.md`. Other workflows, skill-pack references, and durable ledgers stay closed until a trigger in `rules/BOOTSTRAP.md` matches.

The default DAG is `repo-explorer`, then `kernel-dev` when a change is required. Review and other workers are added only for a recorded reason. Cheap read-only R0/R1 lookups stay in the main session. Substantial non-main work goes to a sub-agent with a short upstream summary and file paths. If sub-agents are unavailable, that substantial work is blocked.

## Installation

Install the runtime skill with `scripts/install_skill.py`. The script copies `SKILL.md`, `workflows/`, `scripts/`, `references/`, and `assets/` into a directory named `agent-group`. It leaves `examples/`, `tests/`, `ROADMAP.html`, and the repository docs in the checkout.

```bash
git clone https://github.com/BrokeDudeAbula/agent-group-orchestrator.git
cd agent-group-orchestrator
python3 scripts/install_skill.py --dest ~/.claude/skills
```

The same command works for the other host skills directories below. Pass the skills directory, or a path that already ends in `agent-group`. Add `--force` to replace an existing install. Add `--dry-run` to print the copy plan.

To copy by hand, copy only those five paths:

```bash
dest=~/.claude/skills/agent-group
mkdir -p "$dest"
cp SKILL.md "$dest/"
cp -R workflows scripts references assets "$dest/"
```

Claude Code also loads a project skill from `.claude/skills/agent-group/`. Use the same install command for the other hosts:

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

- `current/`: active goal, tasks, and worker evidence. Archived at phase end.
- `memory/`: compact project facts, a ledger index, and durable ledgers with a summary plus recent tail.
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
| `compact_memory.py` | Archive `current/` and roll durable ledgers. |
| `install_skill.py` | Copy the runtime skill without examples, tests, or `ROADMAP.html`. |
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
