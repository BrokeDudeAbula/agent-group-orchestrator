---
name: agent-group-init
description: Use when Codex should initialize, scaffold, or migrate a project-local .codex/agent_group workspace from the Agent Group Orchestrator plugin templates.
---

# Agent Group Init

Use this skill to create a new agent group instance in a target repository.

## Workflow

1. Confirm the target path, defaulting to `.codex/agent_group`.
2. Inspect whether the target already exists.
3. If it exists, run `scripts/validate_agent_group.py <target>` and propose a migration instead of overwriting.
4. If it does not exist, run:

```bash
python3 scripts/init_agent_group.py --target <target> --project-name <name>
```

5. Validate:

```bash
python3 scripts/validate_agent_group.py <target>
```

6. Report created files and any follow-up project-specific fields the user should fill in.

## Reference Loading

- Read `references/directory-contract.md` for required structure.
- Read `references/worker-registry.md` if custom workers are requested.

## Guardrails

- Do not overwrite an existing instance unless the user explicitly requests `--force`.
- Keep project-specific goals in the target instance, not in plugin templates.

