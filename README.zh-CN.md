[English](README.md) | 中文

# Agent Group Orchestrator

面向项目本地多智能体协作的可移植技能包。一个技能负责初始化、编排、记忆同步和审查。运行状态留在目标项目里。

## 状态放在哪里

- Cursor、OpenCode、Grok Build 及同类宿主：`.agent_group/`
- Claude Code：`.claude/agent_group/`
- Codex：`.codex/agent_group/`

## 安装

用安装脚本复制运行时，或只复制下面这五项。脚本会写入名为 `agent-group` 的目录，并把 `examples/`、`tests/`、`ROADMAP.html` 和这些说明留在原仓库。

```bash
git clone https://github.com/BrokeDudeAbula/agent-group-orchestrator.git
cd agent-group-orchestrator
python3 scripts/install_skill.py --dest ~/.claude/skills
```

复制的路径：`SKILL.md`、`workflows/`、`scripts/`、`references/`、`assets/`。传入 skills 目录，或一个已经以 `agent-group` 结尾的路径。`--dry-run` 只打印计划。`--force` 覆盖已有安装。

同一条命令也适用于 `~/.cursor/skills`、`~/.agents/skills`（Codex，也可作为通用用户路径）、`~/.config/opencode/skills` 和 `~/.grok/skills`。项目内安装使用同名目录，放在 `.claude/skills/`、`.cursor/skills/` 或 `.agents/skills/`、`.opencode/skills/`、`.grok/skills/` 下。复制完成后新开一个会话。

手工复制：

```bash
dest=~/.claude/skills/agent-group
mkdir -p "$dest"
cp SKILL.md "$dest/"
cp -R workflows scripts references assets "$dest/"
```

## 初始化并触发

在目标项目中运行：

```bash
python3 /path/to/agent-group/scripts/init_agent_group.py --project-name my-project
```

不传 `--target` 时，初始化使用上面的宿主默认路径。可用 `--backend claude-code`、`--backend codex`、`--backend neutral` 或 `--target <path>` 明确指定。要查找已经存在的实例，运行 `python3 /path/to/agent-group/scripts/agent_group_paths.py --backend auto --json`。若只有一个标准实例，解析器会选用它。

然后可以用这类提示：

```text
Initialize an agent group workspace for this repo.
Use agent-group auto-orchestrate mode for this goal: <goal>.
Validate this repo's agent group memory structure.
Review this agent group worker output and memory update.
```

## 接下来

`SKILL.md` 会加载 `workflows/init.md`、`workflows/orchestrate.md`、`workflows/memory-sync.md`、`workflows/review.md` 中的一个，然后停止。贡献者检查见 [AGENTS.md](AGENTS.md)。许可证：[MIT](LICENSE)。
