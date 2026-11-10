English | [中文](README.zh-CN.md)

# Agent Group Orchestrator

A portable skill pack for project-local multi-agent work. One skill routes initialization, orchestration, memory sync, and review. Live state stays in the target project.

## Where state lives

- Cursor, OpenCode, Grok Build, and similar hosts: `.agent_group/`
- Claude Code: `.claude/agent_group/`
- Codex: `.codex/agent_group/`

## Install

Copy the runtime with the install script, or copy the five paths below. The script writes an `agent-group` directory and leaves `examples/`, `tests/`, `ROADMAP.html`, and these docs in the checkout.

```bash
git clone https://github.com/BrokeDudeAbula/agent-group-orchestrator.git
cd agent-group-orchestrator
python3 scripts/install_skill.py --dest ~/.claude/skills
```

Copied paths: `SKILL.md`, `workflows/`, `scripts/`, `references/`, and `assets/`. Pass a skills directory, or a path that already ends in `agent-group`. `--dry-run` prints the plan. `--force` replaces an existing install.

The same command works for `~/.cursor/skills`, `~/.agents/skills` (Codex, and a portable user path), `~/.config/opencode/skills`, and `~/.grok/skills`. A project install uses that same folder name under `.claude/skills/`, `.cursor/skills/` or `.agents/skills/`, `.opencode/skills/`, or `.grok/skills/`. Start a new session after copying.

Hand copy:

```bash
dest=~/.claude/skills/agent-group
mkdir -p "$dest"
cp SKILL.md "$dest/"
cp -R workflows scripts references assets "$dest/"
```

## Initialize and trigger

From the target project:

```bash
python3 /path/to/agent-group/scripts/init_agent_group.py --project-name my-project
```

With no `--target`, initialization uses the host default above. Choose explicitly with `--backend claude-code`, `--backend codex`, `--backend neutral`, or `--target <path>`. To find an instance that already exists, run `python3 /path/to/agent-group/scripts/agent_group_paths.py --backend auto --json`. That resolver prefers the only standard instance when just one is present.

Then use prompts such as:

```text
Initialize an agent group workspace for this repo.
Use agent-group auto-orchestrate mode for this goal: <goal>.
Validate this repo's agent group memory structure.
Review this agent group worker output and memory update.
```

## Next

`SKILL.md` loads one of `workflows/init.md`, `workflows/orchestrate.md`, `workflows/memory-sync.md`, or `workflows/review.md`, then stops. Contributor checks are in [AGENTS.md](AGENTS.md). License: [MIT](LICENSE).
