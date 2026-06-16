# Repository Guidelines

## Project Structure & Module Organization
This repository packages a Codex plugin for project-local multi-agent orchestration. Core skill entry points live in `skills/`, with one directory per workflow such as `agent-group-init`, `agent-group-orchestrate`, `agent-group-memory-sync`, and `agent-group-review`. Reusable policy and contract documents live in `references/`. Starter instance templates are under `assets/templates/instance/`; keep them generic and free of project-specific runtime state. `scripts/` contains deterministic Python helpers for initialization, validation, task graph rendering, and memory compaction. `examples/sample/` is the regression and documentation fixture for a complete agent group instance.

## Build, Test, and Development Commands
There is no compiled build step. Use the scripts directly:

```bash
python3 scripts/init_agent_group.py --target /tmp/agent_group_demo --project-name demo
python3 scripts/validate_agent_group.py /tmp/agent_group_demo
python3 scripts/validate_agent_group.py --strict examples/sample
python3 scripts/render_task_dag.py examples/sample/current/tasks.csv
python3 scripts/compact_memory.py --target /tmp/agent_group_demo --archive-name 20260616_demo --dry-run
```

`init_agent_group.py` creates a target instance from templates. `validate_agent_group.py --strict` is the main regression check before submitting changes. `render_task_dag.py` verifies task dependency metadata. Run `compact_memory.py` with `--dry-run` first when testing archival behavior.

## Coding Style & Naming Conventions
Python scripts use standard-library-only Python 3, four-space indentation, `pathlib.Path`, type hints, and small single-purpose functions. Keep CLI messages concise and actionable. Markdown files should use stable headings because validators check exact section names. Worker output files should follow `<task_id>_<worker>.md`, for example `SMP-20260616-01_repo-explorer.md`. Task statuses are limited to `todo`, `in_progress`, `blocked`, `review`, `done`, and `dropped`.

## Testing Guidelines
Add or update fixtures in `examples/sample/` when changing schemas, validators, templates, or routing policy. Always run strict validation against `examples/sample` and at least one freshly initialized `/tmp` instance. If you change `current/tasks.csv`, confirm dependency rendering still works.

## Commit & Pull Request Guidelines
Use short, English, imperative commit subjects that match the existing history, such as `Document plugin usage`, `Document memory lifecycle boundaries`, or `Harden agent group workflow contracts`. Prefer a capitalized action verb (`Add`, `Update`, `Document`, `Harden`, `Validate`, `Fix`) followed by the affected workflow or artifact. Keep each commit to one focused change, write in present tense, omit trailing punctuation, and do not use Conventional Commit prefixes such as `feat:` or `fix:` unless the repository explicitly adopts them later. If a body is needed, explain why the change is necessary and call out compatibility or validation details. Pull requests should describe the workflow affected, list validation commands run, mention schema or template compatibility impacts, and link related issues. Include screenshots only when rendered documentation or diagrams change.

## Security & Configuration Tips
Do not store live project memory, credentials, model paths, or host-specific state in the plugin root. Runtime state belongs in a target repository’s `.codex/agent_group/`. Keep templates neutral and scrub example outputs before committing.
