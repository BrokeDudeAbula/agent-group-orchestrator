---
name: agent-group
description: Use when initializing, orchestrating, reviewing, or synchronizing memory for a project-local agent group. Covers scaffolding .agent_group, .claude/agent_group, or .codex/agent_group; auto-orchestration with workers, task DAGs, and risk gates; compacting or validating memory; and reviewing worker output, routing, or ledgers.
---

# Agent Group

This skill pack coordinates project-local multi-agent work. Runtime state stays in the target project. Scripts, workflows, references, templates, and examples stay in the skill pack.

`<skill-root>` is the directory that contains this file. Resolve it from the loaded skill location. Do not use `CLAUDE_PLUGIN_ROOT` to find scripts, templates, references, or workflows.

## Route by Intent

Load one workflow, for the step you are about to do. Paths below are relative to `<skill-root>`.

| User intent | Load |
| --- | --- |
| Initialize, scaffold, or migrate an agent group workspace | `workflows/init.md` |
| Run or design auto-orchestration, worker selection, a task DAG, or risk gates | `workflows/orchestrate.md` |
| Update, compact, archive, or validate agent group memory | `workflows/memory-sync.md` |
| Review worker output, routing, a memory update, or task evidence | `workflows/review.md` |

Stop after that one workflow. Load another workflow only when its step is the work in front of you. Do not preload references named inside a workflow.

## Startup reads

When an instance already exists, the next files are only:

- `rules/BOOTSTRAP.md`
- `current/STATE.md`

Both paths are inside the instance. The workflow and `rules/BOOTSTRAP.md` name any later file and the trigger for opening it. Do not open a file that has no matching trigger.

Instance `rules/` are the runtime policy. Do not also open the skill-pack `references/` copy of the same topic.

## Instance Location

Live state belongs in the target project, never inside the skill pack:

- Cursor, OpenCode, Grok Build, and similar hosts: `.agent_group/`
- Claude Code: `.claude/agent_group/`
- Codex: `.codex/agent_group/`

Resolve the active instance from the target project:

```bash
python3 <skill-root>/scripts/agent_group_paths.py --backend auto --json
```

Pass `--root <target-project>` when the shell is not already at that project. Pass `--backend claude-code` or `--backend codex` on those hosts, and `--backend neutral` when the instance must be `.agent_group/` even if other host signals are present.
