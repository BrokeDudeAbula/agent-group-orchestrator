# Repository Guidelines

## Project Structure & Module Organization
This repository is a portable skill pack for project-local multi-agent orchestration. `SKILL.md` is the only skill entry and routes by user intent to `workflows/init.md`, `workflows/orchestrate.md`, `workflows/memory-sync.md`, and `workflows/review.md`. Reusable policy and contract documents live in `references/`. Starter instance templates are under `assets/templates/instance/`; keep them generic and free of project-specific runtime state. `scripts/` contains deterministic Python helpers for initialization, validation, path resolution, task graph rendering, and memory compaction. `examples/sample/` is the regression and documentation fixture for a complete agent group instance.

## Build, Test, and Development Commands
There is no compiled build step. Use the scripts directly:

```bash
python3 scripts/init_agent_group.py --backend claude-code --root /tmp/agent_group_demo --project-name demo
python3 scripts/init_agent_group.py --backend neutral --root /tmp/agent_group_neutral --project-name demo
python3 scripts/validate_agent_group.py /tmp/agent_group_demo/.claude/agent_group
python3 scripts/validate_agent_group.py --strict examples/sample
python3 scripts/render_task_dag.py examples/sample/current/tasks.csv
python3 scripts/compact_memory.py --target /tmp/agent_group_demo/.claude/agent_group --archive-name 20260616_demo --dry-run
python3 scripts/agent_group_paths.py --backend auto --json
python3 scripts/check_public_safety.py --git-history .
python3 -m unittest discover -s tests
```

`init_agent_group.py` creates a target instance from templates. Without `--target`, it uses the host default: `.claude/agent_group` for Claude Code, `.codex/agent_group` for Codex, and `.agent_group` otherwise. An existing single standard instance is preferred by `agent_group_paths.py` when resolving, not when initializing. `validate_agent_group.py --strict` is the main regression check before submitting changes. `render_task_dag.py` verifies task dependency metadata. `check_public_safety.py` rejects credentials, host-specific paths, runtime identifiers, and pasted task prompts before publication. Run `compact_memory.py` with `--dry-run` first when testing archival behavior.

## Coding Style & Naming Conventions
Python scripts use standard-library-only Python 3, four-space indentation, `pathlib.Path`, type hints, and small single-purpose functions. Keep CLI messages concise and actionable. Markdown files should use stable headings because validators check exact section names. Worker output files should follow `<task_id>_<worker>.md`, for example `SMP-20260616-01_repo-explorer.md`. Task statuses are limited to `todo`, `in_progress`, `blocked`, `review`, `done`, and `dropped`. Prefer host-neutral wording in the skill and contracts; name specific hosts only when describing adapter behavior.

## Testing Guidelines
Add or update fixtures in `examples/sample/` when changing schemas, validators, templates, routing policy, or public-safety rules. Always run strict validation against `examples/sample`, at least one freshly initialized `/tmp` instance, the public-safety scan, and its unit tests. If you change `current/tasks.csv`, confirm dependency rendering still works. When changing path resolution, cover `.agent_group/`, `.claude/agent_group/`, and `.codex/agent_group/`.

## Commit & Pull Request Guidelines
Use short, English, imperative commit subjects that match the existing history, such as `Document plugin usage`, `Document memory lifecycle boundaries`, or `Harden agent group workflow contracts`. Prefer a capitalized action verb (`Add`, `Update`, `Document`, `Harden`, `Validate`, `Fix`) followed by the affected workflow or artifact. Keep each commit to one focused change, write in present tense, omit trailing punctuation, and do not use Conventional Commit prefixes such as `feat:` or `fix:` unless the repository explicitly adopts them later. If a body is needed, explain why the change is necessary and call out compatibility or validation details. Pull requests should describe the workflow affected, list validation commands run, mention schema or template compatibility impacts, and link related issues. Include screenshots only when rendered documentation or diagrams change.

## Security & Configuration Tips
Do not store live project memory, credentials, model paths, or host-specific state in the skill pack. Runtime state belongs in a target repository’s `.agent_group/`, `.claude/agent_group/`, or `.codex/agent_group/`. Keep templates neutral and scrub example outputs before committing.
