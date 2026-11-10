# Agent Group Init

Use this workflow to create a new agent group instance in a target repository.

`<skill-root>` is the directory that contains `SKILL.md`. Script and reference paths below are relative to that directory. Run initialization against the target project so the instance is not created inside the skill pack.

## Instance Path Resolution

Resolve the target path in this order:

1. Explicit path from the user.
2. An existing standard instance:
   - `.agent_group/`
   - `.claude/agent_group/`
   - `.codex/agent_group/`
3. If none exists, choose the host default:
   - Claude Code → `.claude/agent_group/`
   - Codex → `.codex/agent_group/`
   - Cursor, OpenCode, Grok Build, and similar hosts → `.agent_group/`
4. If more than one standard instance exists and the user did not choose, ask which instance to use.

You can also resolve with:

```bash
python3 <skill-root>/scripts/agent_group_paths.py --backend auto --json
```

## Workflow

1. Confirm the target path using the resolution rules above.
2. Inspect whether the target already exists.
3. If it exists, run `python3 <skill-root>/scripts/validate_agent_group.py <target>` and propose a migration instead of overwriting.
4. If it does not exist, run the script from the target repository root (or pass `--root <repo-root>`), so the default instance path never lands inside the skill pack:

```bash
python3 <skill-root>/scripts/init_agent_group.py --backend auto --project-name <name>
# or with an explicit path:
python3 <skill-root>/scripts/init_agent_group.py --target <target> --project-name <name>
```

Pass `--backend claude-code` on Claude Code and `--backend codex` on Codex. Pass `--backend neutral` for `.agent_group/` on Cursor, OpenCode, Grok Build, and similar hosts. `--backend auto` follows those host signals and otherwise selects `.agent_group/`.

5. Validate:

```bash
python3 <skill-root>/scripts/validate_agent_group.py <target>
```

6. Report created files and any follow-up project-specific fields the user should fill in.

## Reference Loading

- Read `<skill-root>/references/directory-contract.md` for required structure.
- Read `<skill-root>/references/worker-registry.md` if custom workers are requested.

## Guardrails

- Do not overwrite an existing instance unless the user explicitly requests `--force`.
- Keep project-specific goals in the target instance, not in `<skill-root>/assets/templates/`.
- Do not use more than one live instance for the same project without an explicit user choice.
