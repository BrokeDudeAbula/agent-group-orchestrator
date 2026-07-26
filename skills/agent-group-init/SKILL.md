---
name: agent-group-init
description: Use when the host agent should initialize, scaffold, or migrate a project-local agent_group workspace (.claude/agent_group or .codex/agent_group) from the Agent Group Orchestrator plugin templates.
---

# Agent Group Init

Use this skill to create a new agent group instance in a target repository.

## Instance Path Resolution

Resolve the target path in this order:

1. Explicit path from the user.
2. An existing standard instance:
   - `.claude/agent_group/`
   - `.codex/agent_group/`
3. If neither exists, choose the backend default:
   - Claude Code host → `.claude/agent_group/`
   - Codex host → `.codex/agent_group/`
4. If both exist and the user did not choose, ask which instance to use.

You can also resolve with:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/agent_group_paths.py --backend auto
# or, when the plugin root is known as a checkout path:
python3 scripts/agent_group_paths.py --backend auto
```

## Workflow

1. Confirm the target path using the resolution rules above.
2. Inspect whether the target already exists.
3. If it exists, run `scripts/validate_agent_group.py <target>` and propose a migration instead of overwriting.
4. If it does not exist, run the script from the target repository root (or pass `--root <repo-root>`), so the default instance path never lands inside the plugin root:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_agent_group.py --backend auto --project-name <name>
# or with an explicit path:
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_agent_group.py --target <target> --project-name <name>
```

When the plugin root is known as a checkout path, replace `${CLAUDE_PLUGIN_ROOT}` with that path. Prefer `--backend claude-code` when running inside Claude Code, and `--backend codex` when running inside Codex.

5. Validate:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_agent_group.py <target>
```

6. Report created files and any follow-up project-specific fields the user should fill in.

## Reference Loading

- Read `references/directory-contract.md` for required structure.
- Read `references/worker-registry.md` if custom workers are requested.

## Guardrails

- Do not overwrite an existing instance unless the user explicitly requests `--force`.
- Keep project-specific goals in the target instance, not in plugin templates.
- Do not mix two live instances for the same project without an explicit user choice.
