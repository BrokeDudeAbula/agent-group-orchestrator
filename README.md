# Agent Group Orchestrator

Reusable, backend-neutral plugin for project-local multi-agent orchestration.

This plugin turns a project-local `agent_group` workflow into a generic package:

- `skills/` contains the host-facing workflows (Claude Code and Codex).
- `references/` contains reusable policies and contracts loaded on demand.
- `assets/templates/instance/` contains a starter `agent_group` instance.
- `scripts/` contains deterministic initialization, validation, path resolution, and compaction helpers.
- `examples/sample/` contains a neutral sample instance for regression and documentation.

The plugin should not keep live project state at its root. Project-specific state belongs in a target repository instance:

- Claude Code: `.claude/agent_group/`
- Codex: `.codex/agent_group/`

## 执行模型

`agent-group` 的默认模式是 `auto-orchestrate`。主 agent 只作为 `main-orchestrator` 监督任务：负责目标澄清、任务拆解、worker 选择、sub-agent 派发、进度监督、风险门禁、记忆同步、证据抽查和结果汇总。

除 `main-orchestrator` 以外，所有被选中的 worker 都必须通过兼容的 sub-agent 后端执行。规则按后端中立方式描述，同时适配 Claude Code CLI 与 Codex 的 sub-agent 机制。主 agent 不应直接代替 worker 做开发、测试、benchmark、代码 review、仓库调研、竞品调研或架构分析；如果当前环境没有可用 sub-agent 机制，应把任务标记为 blocked 或要求用户切换到支持 sub-agent 的后端。

## 使用方式

### 1. 获取插件源码

```bash
git clone <agent-group-orchestrator-repository-url>
cd agent-group-orchestrator
```

这个仓库同时是 Claude Code plugin root 与 Codex plugin root：

- Claude Code 清单位于 `.claude-plugin/plugin.json`
- Codex 清单位于 `.codex-plugin/plugin.json`

### 2. 作为 Claude Code 插件安装

#### 2.1 会话级加载（开发调试）

```bash
claude plugin validate /path/to/agent-group-orchestrator
claude --plugin-dir /path/to/agent-group-orchestrator
```

#### 2.2 本地 marketplace 持久安装（推荐）

仓库本身是 plugin root，不是 marketplace root。常见个人布局：

```text
~/claude-marketplaces/personal/
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    └── agent-group-orchestrator -> /path/to/agent-group-orchestrator
```

`marketplace.json` 示例：

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "personal",
  "description": "Personal local plugins",
  "owner": {
    "name": "Local developer"
  },
  "plugins": [
    {
      "name": "agent-group-orchestrator",
      "description": "Project-local multi-agent orchestration workflows",
      "source": "./plugins/agent-group-orchestrator",
      "category": "development"
    }
  ]
}
```

然后安装：

```bash
claude plugin marketplace add ~/claude-marketplaces/personal
claude plugin install agent-group-orchestrator@personal
claude plugin list
```

安装后请开启一个新的 Claude Code 会话，让 skills 重新加载。

### 3. 作为 Codex 本地插件安装

Codex 插件需要通过 marketplace 入口安装。最常见的个人本地插件布局是：

```text
~/.agents/plugins/marketplace.json
~/plugins/agent-group-orchestrator/
```

将本仓库放到 `~/plugins/agent-group-orchestrator` 后，在 `~/.agents/plugins/marketplace.json` 中加入插件条目：

```json
{
  "name": "personal",
  "interface": {
    "displayName": "Personal"
  },
  "plugins": [
    {
      "name": "agent-group-orchestrator",
      "source": {
        "source": "local",
        "path": "./plugins/agent-group-orchestrator"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Developer Tools"
    }
  ]
}
```

然后安装插件：

```bash
codex plugin add agent-group-orchestrator@personal
```

安装后请开启一个新的 Codex 线程，让宿主重新加载插件提供的 skills。

> 说明：本仓库不是 marketplace root，因此不要直接把本仓库路径传给 `codex plugin marketplace add` 或 `claude plugin marketplace add`。如果你使用团队级 marketplace，应在团队 marketplace 的 `plugins[]` 中引用本插件目录。

### 4. 初始化项目本地 agent_group 实例

路径解析规则：

1. 显式 `--target`
2. 已有 `.claude/agent_group` 或 `.codex/agent_group`
3. 按 `--backend` / 宿主环境选择默认路径

Claude Code 默认：

```bash
python3 /path/to/agent-group-orchestrator/scripts/init_agent_group.py \
  --backend claude-code \
  --project-name <your-project-name>
# 等价于创建 .claude/agent_group
```

Codex 默认：

```bash
python3 /path/to/agent-group-orchestrator/scripts/init_agent_group.py \
  --backend codex \
  --project-name <your-project-name>
# 等价于创建 .codex/agent_group
```

显式路径：

```bash
python3 /path/to/agent-group-orchestrator/scripts/init_agent_group.py \
  --target .claude/agent_group \
  --project-name <your-project-name>
```

初始化后校验：

```bash
python3 /path/to/agent-group-orchestrator/scripts/validate_agent_group.py .claude/agent_group
# 或
python3 /path/to/agent-group-orchestrator/scripts/validate_agent_group.py .codex/agent_group
```

严格校验记忆文件形态：

```bash
python3 /path/to/agent-group-orchestrator/scripts/validate_agent_group.py --strict .claude/agent_group
```

解析当前应使用的实例路径：

```bash
python3 /path/to/agent-group-orchestrator/scripts/agent_group_paths.py --backend auto
python3 /path/to/agent-group-orchestrator/scripts/agent_group_paths.py --backend auto --json
```

### 5. 触发工作流

插件安装并新开会话后，可以直接用自然语言触发对应 skill：

```text
Initialize an agent group workspace for this repo.
```

用于初始化项目本地 `agent_group` 实例。

```text
Use agent-group auto-orchestrate mode for this goal: <your-goal>
```

用于按 worker registry、routing policy、sub-agent execution、risk gate 和 memory sync 规则拆解并推进任务。

```text
Validate this repo's agent group memory structure.
```

用于校验当前项目的 agent group 结构和记忆文件一致性。

```text
Review this agent group worker output and memory update.
```

用于对 worker 输出、风险门禁、证据链和记忆同步结果做 review。

### 6. 常用维护命令

从 `current/tasks.csv` 渲染 Mermaid 任务图；如果任务表包含 `depends_on` 列，脚本会生成依赖边：

```bash
python3 /path/to/agent-group-orchestrator/scripts/render_task_dag.py \
  .claude/agent_group/current/tasks.csv
```

归档当前阶段记忆，先 dry-run：

```bash
python3 /path/to/agent-group-orchestrator/scripts/compact_memory.py \
  --target .claude/agent_group \
  --archive-name 20260616_example \
  --dry-run
```

确认无误后执行归档：

```bash
python3 /path/to/agent-group-orchestrator/scripts/compact_memory.py \
  --target .claude/agent_group \
  --archive-name 20260616_example
```

归档脚本默认会重建空的 `current/STATE.md`、`current/epic.md`、`current/acceptance.md` 和 `current/tasks.csv`，确保实例仍可通过严格校验。只有在另一个工具会立即重建这些 hot state 文件时，才使用 `--no-reset-current`。

公开或提交前扫描当前工作区中的凭证、真实用户路径、主机标识、线程 UUID 和误粘贴任务提示：

```bash
python3 scripts/check_public_safety.py .
python3 scripts/check_public_safety.py --git-history .
```

第一条命令覆盖未跟踪文本文件，以便在 `git add` 前发现风险；第二条还会检查所有本地可达历史及提交元数据，应用于正式发布前。真实项目报告和运行时状态应保存在插件仓库之外。

### 7. 目录约定

项目内的运行时状态应放在目标仓库的 `.claude/agent_group/` 或 `.codex/agent_group/`，不要写回插件根目录。

- `current/STATE.md`：当前活跃目标、阶段、阻塞点和下一步。
- `current/tasks.csv`：当前 epic 的任务清单。
- `current/agent_outputs/`：当前阶段 worker 输出和证据。
- `memory/TASK_LEDGER.md`：长期任务台账。
- `memory/PROGRESS_LEDGER.md`：追加式进展记录。
- `memory/DECISIONS.md`：架构与流程决策。
- `memory/RISKS.md`：风险、缓解和关闭记录。
- `rules/`：项目本地 worker、sub-agent 执行、路由、同步和 runbook 规则。
